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
from almanach.validators import instance_validator

LOG = log.getLogger(__name__)


class EntityController(base_controller.BaseController):

    def __init__(self, database_adapter):
        self.database_adapter = database_adapter

    def update_active_instance_entity(self, instance_id, **kwargs):
        try:
            instance_validator.InstanceValidator().validate_update(kwargs)
            instance = self.database_adapter.get_active_entity(instance_id)
            self._update_instance_object(instance, **kwargs)
            self.database_adapter.update_active_entity(instance)
            return instance
        except exception.EntityNotFoundException as e:
            LOG.error("Instance %s is not in the database yet.", instance_id)
            raise e

    def update_inactive_entity(self, instance_id, start, end, **kwargs):
        inactive_entities = self.database_adapter.get_all_entities_by_id_and_date(instance_id, start, end)
        if len(inactive_entities) > 1:
            raise exception.MultipleEntitiesMatchingQueryException()
        if len(inactive_entities) < 1:
            raise exception.EntityNotFoundException(
                    "InstanceId: {0} Not Found with start".format(instance_id))
        entity = inactive_entities[0]
        entity_update = self._transform_attribute_to_match_entity_attribute(**kwargs)
        self.database_adapter.update_closed_entity(entity=entity, data=entity_update)
        start = entity_update.get('start') or start
        end = entity_update.get('end') or end
        return self.database_adapter.get_all_entities_by_id_and_date(instance_id, start, end)[0]

    def entity_exists(self, entity_id):
        return self.database_adapter.count_entity_entries(entity_id=entity_id) >= 1

    def get_all_entities_by_id(self, entity_id):
        if not self.entity_exists(entity_id=entity_id):
            raise exception.EntityNotFoundException("Entity not found")
        return self.database_adapter.get_all_entities_by_id(entity_id=entity_id)

    def list_entities(self, project_id, start, end):
        return self.database_adapter.get_all_entities_by_project(project_id, start, end)

    def _update_instance_object(self, instance, **kwargs):
        for key, value in self._transform_attribute_to_match_entity_attribute(**kwargs).items():
            setattr(instance, key, value)
            LOG.info("Updating entity for instance '%s' with %s=%s", instance.entity_id, key, value)
