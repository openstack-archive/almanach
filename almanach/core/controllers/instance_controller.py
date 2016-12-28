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
        self.config = config
        self.database_adapter = database_adapter

    def create_instance(self, instance_id, tenant_id, create_date, name, flavor, image_meta=None, metadata=None):
        create_date = self._validate_and_parse_date(create_date)
        image_meta = self._filter_image_meta(image_meta)
        LOG.info("Instance %s created (tenant %s; flavor %s; image_meta %s) on %s",
                 instance_id, tenant_id, flavor, image_meta, create_date)

        if self._fresher_entity_exists(instance_id, create_date):
            LOG.warning("instance %s already exists with a more recent entry", instance_id)
            return

        entity = model.Instance(
            entity_id=instance_id,
            project_id=tenant_id,
            last_event=create_date,
            start=create_date,
            end=None,
            name=name,
            flavor=flavor,
            image_meta=image_meta,
            metadata=self._filter_metadata(metadata))

        self.database_adapter.insert_entity(entity)

    def delete_instance(self, instance_id, delete_date):
        if not self.database_adapter.has_active_entity(instance_id):
            raise exception.EntityNotFoundException(
                    "InstanceId: {0} Not Found".format(instance_id))

        delete_date = self._validate_and_parse_date(delete_date)
        LOG.info("Instance %s deleted on %s", instance_id, delete_date)
        self.database_adapter.close_active_entity(instance_id, delete_date)

    def resize_instance(self, instance_id, flavor, resize_date):
        resize_date = self._validate_and_parse_date(resize_date)
        LOG.info("Instance %s resized to flavor %s on %s", instance_id, flavor, resize_date)
        try:
            instance = self.database_adapter.get_active_entity(instance_id)
            if flavor != instance.flavor:
                self.database_adapter.close_active_entity(instance_id, resize_date)
                instance.flavor = flavor
                instance.start = resize_date
                instance.end = None
                instance.last_event = resize_date
                self.database_adapter.insert_entity(instance)
        except exception.EntityNotFoundException as e:
            LOG.error("Trying to resize an instance with id '%s' not in the database yet.", instance_id)
            raise e

    def rebuild_instance(self, instance_id, rebuild_date, image_meta):
        rebuild_date = self._validate_and_parse_date(rebuild_date)
        instance = self.database_adapter.get_active_entity(instance_id)
        image_meta = self._filter_image_meta(image_meta)
        LOG.info("Instance %s rebuilt for tenant %s with %s on %s",
                 instance_id, instance.project_id, image_meta, rebuild_date)

        if instance.image_meta != image_meta:
            self.database_adapter.close_active_entity(instance_id, rebuild_date)
            instance.image_meta = image_meta
            instance.start = rebuild_date
            instance.end = None
            instance.last_event = rebuild_date
            self.database_adapter.insert_entity(instance)

    def list_instances(self, project_id, start, end):
        return self.database_adapter.get_all_entities_by_project(project_id, start, end, model.Instance.TYPE)

    def _filter_metadata(self, metadata):
        return self._filter(metadata, self.config.entities.instance_metadata)

    def _filter_image_meta(self, image_meta):
        return self._filter(image_meta, self.config.entities.instance_image_meta)

    @staticmethod
    def _filter(d, whitelist):
        if d:
            return {key: value for key, value in d.items() if key in whitelist}
        return {}
