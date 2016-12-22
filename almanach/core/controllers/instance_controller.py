# Copyright 2016 Internap.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_log import log

from almanach.core.controllers import base_controller
from almanach.core import exception
from almanach.core import model

LOG = log.getLogger(__name__)


class InstanceController(base_controller.BaseController):

    def __init__(self, config, database_adapter):
        self.database_adapter = database_adapter
        self.metadata_whitelist = config.resources.device_metadata_whitelist

    def create_instance(self, instance_id, tenant_id, create_date, flavor, os_type, distro, version, name, metadata):
        create_date = self._validate_and_parse_date(create_date)
        LOG.info("instance %s created in project %s (flavor %s; distro %s %s %s) on %s",
                 instance_id, tenant_id, flavor, os_type, distro, version, create_date)

        if self._fresher_entity_exists(instance_id, create_date):
            LOG.warning("instance %s already exists with a more recent entry", instance_id)
            return

        filtered_metadata = self._filter_metadata_with_whitelist(metadata)

        entity = model.Instance(instance_id, tenant_id, create_date, None, flavor,
                                {"os_type": os_type, "distro": distro,
                                 "version": version},
                                create_date, name, filtered_metadata)
        self.database_adapter.insert_entity(entity)

    def delete_instance(self, instance_id, delete_date):
        if not self.database_adapter.has_active_entity(instance_id):
            raise exception.AlmanachEntityNotFoundException(
                    "InstanceId: {0} Not Found".format(instance_id))

        delete_date = self._validate_and_parse_date(delete_date)
        LOG.info("instance %s deleted on %s", instance_id, delete_date)
        self.database_adapter.close_active_entity(instance_id, delete_date)

    def resize_instance(self, instance_id, flavor, resize_date):
        resize_date = self._validate_and_parse_date(resize_date)
        LOG.info("instance %s resized to flavor %s on %s", instance_id, flavor, resize_date)
        try:
            instance = self.database_adapter.get_active_entity(instance_id)
            if flavor != instance.flavor:
                self.database_adapter.close_active_entity(instance_id, resize_date)
                instance.flavor = flavor
                instance.start = resize_date
                instance.end = None
                instance.last_event = resize_date
                self.database_adapter.insert_entity(instance)
        except KeyError as e:
            LOG.error("Trying to resize an instance with id '%s' not in the database yet.", instance_id)
            raise e

    def rebuild_instance(self, instance_id, distro, version, os_type, rebuild_date):
        rebuild_date = self._validate_and_parse_date(rebuild_date)
        instance = self.database_adapter.get_active_entity(instance_id)
        LOG.info("instance %s rebuilded in project %s to os %s %s %s on %s",
                 instance_id, instance.project_id, os_type, distro, version, rebuild_date)

        if instance.os.distro != distro or instance.os.version != version:
            self.database_adapter.close_active_entity(instance_id, rebuild_date)

            instance.os.distro = distro
            instance.os.version = version
            instance.os.os_type = os_type
            instance.start = rebuild_date
            instance.end = None
            instance.last_event = rebuild_date
            self.database_adapter.insert_entity(instance)

    def list_instances(self, project_id, start, end):
        return self.database_adapter.get_all_entities_by_project(project_id, start, end, model.Instance.TYPE)

    def _filter_metadata_with_whitelist(self, metadata):
        return {key: value for key, value in metadata.items() if key in self.metadata_whitelist}
