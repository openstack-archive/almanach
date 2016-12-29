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

from almanach.collector import service
import mock

from almanach.tests.unit import base


class TestServiceFactory(base.BaseTestCase):

    def setUp(self):
        super(TestServiceFactory, self).setUp()
        self.core_factory = mock.Mock()
        self.factory = service.ServiceFactory(self.config, self.core_factory)

    def test_get_service(self):
        self.assertIsInstance(self.factory.get_service(),
                              service.CollectorService)

        self.core_factory.get_instance_controller.assert_called_once()
        self.core_factory.get_volume_controller.assert_called_once()
        self.core_factory.get_volume_type_controller.assert_called_once()
