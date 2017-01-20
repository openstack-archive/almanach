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

import mock

from almanach.core.controllers import application_controller
from almanach.core.controllers import entity_controller
from almanach.core.controllers import instance_controller
from almanach.core.controllers import volume_controller
from almanach.core.controllers import volume_type_controller
from almanach.core import factory

from almanach.tests.unit import base


class TestFactory(base.BaseTestCase):

    def setUp(self):
        super(TestFactory, self).setUp()
        self.storage = mock.Mock()
        self.factory = factory.Factory(self.config, self.storage)

    def test_get_instance_controller(self):
        self.assertIsInstance(self.factory.get_instance_controller(),
                              instance_controller.InstanceController)

    def test_get_volume_controller(self):
        self.assertIsInstance(self.factory.get_volume_controller(),
                              volume_controller.VolumeController)

    def test_get_volume_type_controller(self):
        self.assertIsInstance(self.factory.get_volume_type_controller(),
                              volume_type_controller.VolumeTypeController)

    def test_get_entity_controller(self):
        self.assertIsInstance(self.factory.get_entity_controller(),
                              entity_controller.EntityController)

    def test_get_application_controller(self):
        self.assertIsInstance(self.factory.get_application_controller(),
                              application_controller.ApplicationController)

    def test_bootstrap_storage(self):
        self.assertIsInstance(self.factory.get_instance_controller(),
                              instance_controller.InstanceController)

        self.assertIsInstance(self.factory.get_volume_controller(),
                              volume_controller.VolumeController)

        self.storage.connect.assert_called_once()
