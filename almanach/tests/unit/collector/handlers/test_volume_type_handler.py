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

from almanach.collector.handlers import volume_type_handler
from almanach.tests.unit import base
from almanach.tests.unit.builders import notification as builder


class TestVolumeTypeHandler(base.BaseTestCase):

    def setUp(self):
        super(TestVolumeTypeHandler, self).setUp()
        self.controller = mock.Mock()
        self.volume_type_handler = volume_type_handler.VolumeTypeHandler(self.controller)

    def test_volume_type_created(self):
        notification = builder.VolumeTypeNotificationBuilder()\
            .with_event_type('volume_type.create')\
            .build()

        self.volume_type_handler.handle_events(notification)
        self.controller.create_volume_type.assert_called_once_with(
            notification.payload['volume_types']['id'],
            notification.payload['volume_types']['name']
        )
