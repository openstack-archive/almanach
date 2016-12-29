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

from almanach.collector.handlers import volume_handler
from almanach.tests.unit import base
from almanach.tests.unit.builders import notification as builder


class TestVolumeHandler(base.BaseTestCase):

    def setUp(self):
        super(TestVolumeHandler, self).setUp()
        self.controller = mock.Mock()
        self.volume_handler = volume_handler.VolumeHandler(self.controller)

    def test_volume_created(self):
        notification = builder.VolumeNotificationBuilder() \
            .with_event_type('volume.create.end') \
            .build()

        self.volume_handler.handle_events(notification)

        self.controller.create_volume.assert_called_once_with(
            notification.payload['volume_id'],
            notification.payload['tenant_id'],
            notification.payload['created_at'],
            notification.payload['volume_type'],
            notification.payload['size'],
            notification.payload['display_name'],
        )

    def test_volume_deleted(self):
        notification = builder.VolumeNotificationBuilder() \
            .with_event_type('volume.delete.end') \
            .with_context_value('timestamp', 'a_date') \
            .build()

        self.volume_handler.handle_events(notification)

        self.controller.delete_volume.assert_called_once_with(
            notification.payload['volume_id'],
            notification.context['timestamp'],
        )

    def test_volume_renamed(self):
        notification = builder.VolumeNotificationBuilder() \
            .with_event_type('volume.update.end') \
            .build()

        self.volume_handler.handle_events(notification)

        self.controller.rename_volume.assert_called_once_with(
            notification.payload['volume_id'],
            notification.payload['display_name'],
        )

    def test_volume_renamed_with_exists_event(self):
        notification = builder.VolumeNotificationBuilder() \
            .with_event_type('volume.exists') \
            .build()

        self.volume_handler.handle_events(notification)

        self.controller.rename_volume.assert_called_once_with(
                notification.payload['volume_id'],
                notification.payload['display_name'],
        )

    def test_volume_resized(self):
        notification = builder.VolumeNotificationBuilder() \
            .with_event_type('volume.resize.end') \
            .with_context_value('timestamp', 'a_date') \
            .build()

        self.volume_handler.handle_events(notification)

        self.controller.resize_volume.assert_called_once_with(
            notification.payload['volume_id'],
            notification.payload['size'],
            notification.context['timestamp'],
        )

    def test_volume_attach_empty(self):
        notification = builder.VolumeNotificationBuilder() \
            .with_event_type('volume.attach.end') \
            .with_context_value('timestamp', 'a_date') \
            .build()

        self.volume_handler.handle_events(notification)

        self.controller.attach_volume.assert_called_once_with(
            notification.payload['volume_id'],
            notification.context['timestamp'],
            []
        )

    def test_volume_attach_with_instances(self):
        notification = builder.VolumeNotificationBuilder() \
            .with_event_type('volume.attach.end') \
            .with_context_value('timestamp', 'a_date') \
            .with_instance_attached('instance_id1') \
            .with_instance_attached('instance_id2') \
            .build()

        self.volume_handler.handle_events(notification)

        self.controller.attach_volume.assert_called_once_with(
            notification.payload['volume_id'],
            notification.context['timestamp'],
            ['instance_id1', 'instance_id2']
        )

    def test_volume_detached(self):
        notification = builder.VolumeNotificationBuilder() \
            .with_event_type('volume.detach.end') \
            .with_context_value('timestamp', 'a_date') \
            .build()

        self.volume_handler.handle_events(notification)

        self.controller.detach_volume.assert_called_once_with(
            notification.payload['volume_id'],
            notification.context['timestamp'],
            []
        )
