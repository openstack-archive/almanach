# Copyright 2017 Internap.
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

from almanach.collector.filters import delete_instance_before_completion_filter
from almanach.collector import notification

from almanach.tests.unit import base
from almanach.tests.unit.builders import notification as builder


class TestDeleteInstanceBeforeCompletionFilter(base.BaseTestCase):

    def setUp(self):
        super(TestDeleteInstanceBeforeCompletionFilter, self).setUp()
        self.filter = delete_instance_before_completion_filter.DeleteInstanceBeforeCompletionFilter(self.config)

    def test_with_instance_deleted_quickly(self):
        message = builder.InstanceNotificationBuilder() \
            .with_event_type('compute.instance.delete.end') \
            .with_payload_value('state', 'deleted') \
            .with_payload_value('created_at', '2017-02-05 11:25:01+00:00') \
            .with_payload_value('deleted_at', '2017-02-05T11:34:36.000000') \
            .with_context_value(notification.NotificationMessage.RETRY_COUNTER, 3) \
            .build()

        self.assertTrue(self.filter.ignore_notification(message))

    def test_when_message_was_never_retried(self):
        message = builder.InstanceNotificationBuilder() \
            .with_event_type('compute.instance.delete.end') \
            .with_payload_value('state', 'deleted') \
            .with_payload_value('created_at', '2017-02-05 11:25:01+00:00') \
            .with_payload_value('deleted_at', '2017-02-05T11:34:36.000000') \
            .build()

        self.assertFalse(self.filter.ignore_notification(message))

    def test_with_instance_deleted_later(self):
        message = builder.InstanceNotificationBuilder() \
            .with_event_type('compute.instance.delete.end') \
            .with_payload_value('state', 'deleted') \
            .with_payload_value('created_at', '2017-02-05 11:25:01+00:00') \
            .with_payload_value('deleted_at', '2017-02-05T11:44:36.000000') \
            .with_context_value(notification.NotificationMessage.RETRY_COUNTER, 3) \
            .build()

        self.assertFalse(self.filter.ignore_notification(message))
