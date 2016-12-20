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

from flexmock import flexmock

from almanach.core.controllers import volume_type_controller
from almanach.storage.drivers import base_driver
from almanach.tests.unit import base
from almanach.tests.unit.builder import a
from almanach.tests.unit.builder import volume_type


class VolumeTypeControllerTest(base.BaseTestCase):

    def setUp(self):
        super(VolumeTypeControllerTest, self).setUp()
        self.database_adapter = flexmock(base_driver.BaseDriver)
        self.controller = volume_type_controller.VolumeTypeController(self.database_adapter)

    def test_volume_type_created(self):
        fake_volume_type = a(volume_type())

        (flexmock(self.database_adapter)
         .should_receive("insert_volume_type")
         .with_args(fake_volume_type)
         .once())

        self.controller.create_volume_type(fake_volume_type.volume_type_id, fake_volume_type.volume_type_name)

    def test_get_volume_type(self):
        some_volume = a(volume_type())
        (flexmock(self.database_adapter)
         .should_receive("get_volume_type")
         .and_return(some_volume)
         .once())

        returned_volume_type = self.controller.get_volume_type(some_volume.volume_type_id)

        self.assertEqual(some_volume, returned_volume_type)

    def test_delete_volume_type(self):
        some_volume = a(volume_type())
        (flexmock(self.database_adapter)
         .should_receive("delete_volume_type")
         .once())

        self.controller.delete_volume_type(some_volume.volume_type_id)

    def test_list_volume_types(self):
        some_volumes = [a(volume_type()), a(volume_type())]
        (flexmock(self.database_adapter)
         .should_receive("list_volume_types")
         .and_return(some_volumes)
         .once())

        self.assertEqual(len(self.controller.list_volume_types()), 2)
