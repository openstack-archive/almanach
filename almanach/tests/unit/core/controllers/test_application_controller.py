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
from almanach.tests.unit import base


class TestApplicationController(base.BaseTestCase):

    def setUp(self):
        super(TestApplicationController, self).setUp()
        self.database_adapter = mock.Mock()
        self.controller = application_controller.ApplicationController(self.database_adapter)

    def test_get_application_info(self):
        self.database_adapter.count_entities.return_value = 20
        self.database_adapter.count_active_entities.return_value = 16

        info = self.controller.get_application_info()

        self.assertIsNotNone(info['info']['version'])
        self.assertEqual(20, info['database']['all_entities'])
        self.assertEqual(16, info['database']['active_entities'])

        self.database_adapter.count_entities.assert_called_once()
        self.database_adapter.count_active_entities.assert_called_once()
