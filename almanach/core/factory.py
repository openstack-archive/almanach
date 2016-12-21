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

from almanach.core.controllers import application_controller
from almanach.core.controllers import entity_controller
from almanach.core.controllers import instance_controller
from almanach.core.controllers import volume_controller
from almanach.core.controllers import volume_type_controller
from almanach.storage import storage_driver


class Factory(object):

    def __init__(self, config, storage=None):
        self.config = config
        self.database_driver = None
        self.storage_driver = storage or storage_driver.StorageDriver(self.config).get_database_driver()

    def get_instance_controller(self):
        return instance_controller.InstanceController(self.config, self._get_database_driver())

    def get_volume_controller(self):
        return volume_controller.VolumeController(self.config, self._get_database_driver())

    def get_volume_type_controller(self):
        return volume_type_controller.VolumeTypeController(self._get_database_driver())

    def get_entity_controller(self):
        return entity_controller.EntityController(self._get_database_driver())

    def get_application_controller(self):
        return application_controller.ApplicationController(self._get_database_driver())

    def _get_database_driver(self):
        if not self.database_driver:
            self.database_driver = self.storage_driver
            self.database_driver.connect()
        return self.database_driver
