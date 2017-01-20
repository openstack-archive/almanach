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

from almanach.core.controllers import volume_type_controller

from almanach.tests.unit import base
from almanach.tests.unit.builders.entity import a
from almanach.tests.unit.builders.entity import volume_type


class TestVolumeTypeController(base.BaseTestCase):

    def setUp(self):
        super(TestVolumeTypeController, self).setUp()
        self.database_adapter = mock.Mock()
        self.controller = volume_type_controller.VolumeTypeController(self.database_adapter)

    def test_create_volume_type(self):
        fake_volume_type = a(volume_type())
        self.controller.create_volume_type(fake_volume_type.volume_type_id, fake_volume_type.volume_type_name)
        self.database_adapter.insert_volume_type.assert_called_once_with(fake_volume_type)

    def test_get_volume_type(self):
        some_volume = a(volume_type())
        self.database_adapter.get_volume_type.return_value = some_volume

        a_volume_type = self.controller.get_volume_type(some_volume.volume_type_id)

        self.assertEqual(some_volume, a_volume_type)
        self.database_adapter.get_volume_type.assert_called_once_with(some_volume.volume_type_id)

    def test_delete_volume_type(self):
        some_volume = a(volume_type())
        self.controller.delete_volume_type(some_volume.volume_type_id)
        self.database_adapter.delete_volume_type.assert_called_once_with(some_volume.volume_type_id)

    def test_list_volume_types(self):
        some_volumes = [a(volume_type()), a(volume_type())]
        self.database_adapter.list_volume_types.return_value = some_volumes
        self.assertEqual(len(self.controller.list_volume_types()), 2)
        self.database_adapter.list_volume_types.assert_called_once()
