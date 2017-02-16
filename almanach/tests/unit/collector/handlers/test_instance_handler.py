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

from almanach.collector.handlers import instance_handler
from almanach.core import exception
from almanach.tests.unit import base
from almanach.tests.unit.builders import notification as builder


class TestInstanceHandler(base.BaseTestCase):

    def setUp(self):
        super(TestInstanceHandler, self).setUp()
        self.controller = mock.Mock()
        self.on_delete_filter = mock.Mock()
        self.on_delete_filter.ignore_notification.return_value = False
        self.instance_handler = instance_handler.InstanceHandler(self.controller, self.on_delete_filter)

    def test_instance_created(self):
        notification = builder.InstanceNotificationBuilder()\
            .with_event_type('compute.instance.create.end')\
            .with_image_meta('os_type', 'linux')\
            .with_image_meta('distro', 'ubuntu')\
            .with_image_meta('version', '16.04')\
            .build()

        self.instance_handler.handle_events(notification)

        self.controller.create_instance.assert_called_once_with(
            instance_id=notification.payload['instance_id'],
            tenant_id=notification.payload['tenant_id'],
            create_date=notification.payload['created_at'],
            name=notification.payload['hostname'],
            flavor=notification.payload['instance_type'],
            image_meta=notification.payload['image_meta'],
            metadata=notification.payload['metadata'],
        )

    def test_instance_deleted(self):
        notification = builder.InstanceNotificationBuilder() \
            .with_event_type('compute.instance.delete.end') \
            .with_payload_value('terminated_at', 'a_date') \
            .build()

        self.instance_handler.handle_events(notification)

        self.controller.delete_instance.assert_called_once_with(
            notification.payload['instance_id'],
            notification.payload['terminated_at']
        )

    def test_instance_deleted_but_never_created(self):
        notification = builder.InstanceNotificationBuilder() \
            .with_event_type('compute.instance.delete.end') \
            .with_payload_value('terminated_at', 'a_date') \
            .build()

        self.controller.delete_instance.side_effect = exception.EntityNotFoundException('Instance not found')

        self.assertRaises(exception.EntityNotFoundException,
                          self.instance_handler.handle_events, notification)

        self.controller.delete_instance.assert_called_once_with(
            notification.payload['instance_id'],
            notification.payload['terminated_at']
        )

    def test_instance_in_error_deleted(self):
        self.on_delete_filter.ignore_notification.return_value = True

        notification = builder.InstanceNotificationBuilder() \
            .with_event_type('compute.instance.delete.end') \
            .with_payload_value('terminated_at', 'a_date') \
            .with_payload_value('state', 'error') \
            .build()

        self.controller.delete_instance.side_effect = exception.EntityNotFoundException('Instance not found')
        self.instance_handler.handle_events(notification)

        self.controller.delete_instance.assert_called_once_with(
            notification.payload['instance_id'],
            notification.payload['terminated_at']
        )

    def test_instance_resized(self):
        notification = builder.InstanceNotificationBuilder() \
            .with_event_type('compute.instance.resize.confirm.end') \
            .with_context_value('timestamp', 'a_date') \
            .build()

        self.instance_handler.handle_events(notification)

        self.controller.resize_instance.assert_called_once_with(
            notification.payload['instance_id'],
            notification.payload['instance_type'],
            notification.context.get("timestamp")
        )

    def test_instance_rebuild(self):
        notification = builder.InstanceNotificationBuilder() \
            .with_event_type('compute.instance.rebuild.end') \
            .with_context_value('timestamp', 'a_date') \
            .with_image_meta('os_type', 'linux') \
            .with_image_meta('distro', 'ubuntu') \
            .with_image_meta('version', '16.04') \
            .build()

        self.instance_handler.handle_events(notification)

        self.controller.rebuild_instance.assert_called_once_with(
            instance_id=notification.payload['instance_id'],
            rebuild_date=notification.context.get("timestamp"),
            image_meta=notification.payload['image_meta'],
        )
