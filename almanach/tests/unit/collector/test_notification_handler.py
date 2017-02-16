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

from almanach.collector import notification
from almanach.tests.unit import base


class TestNotificationHandler(base.BaseTestCase):

    def setUp(self):
        super(TestNotificationHandler, self).setUp()

        self.config_fixture.config(retry_delay=0, group='collector')
        self.config_fixture.config(max_retries=3, group='collector')

        self.messaging = mock.Mock()
        self.notifier = mock.Mock()
        self.messaging.get_notifier.return_value = self.notifier
        self.handler = notification.NotificationHandler(self.config, self.messaging)

    def test_retry_counter(self):
        message = notification.NotificationMessage('event_type', dict(), dict(), dict())

        self.assertEqual(0, message.get_retry_counter())

        message.increment_retry_count()
        self.assertEqual(1, message.get_retry_counter())

        message.increment_retry_count()
        self.assertEqual(2, message.get_retry_counter())

    def test_incoming_notifications_are_processed(self):
        event_handler1 = mock.Mock()
        event_handler2 = mock.Mock()

        self.handler.add_event_handler(event_handler1)
        self.handler.add_event_handler(event_handler2)

        self.handler.info(dict(), 'compute.nova01', 'some_event', dict(), dict())

        event_handler1.handle_events.assert_called_once()
        event_handler2.handle_events.assert_called_once()

    def test_failed_notification_are_sent_to_error_queue(self):
        event_handler = mock.Mock()
        event_handler.handle_events.side_effect = Exception()

        self.handler.add_event_handler(event_handler)
        self.handler.info(dict(), 'compute.nova01', 'some_event', dict(), dict())

        self.notifier.error.assert_called_once()

        self.notifier.info.assert_not_called()
        self.notifier.critical.assert_not_called()

    def test_notifications_are_sent_again_to_info_queue_if_under_threshold(self):
        context = {
            notification.NotificationMessage.RETRY_COUNTER: 2
        }

        self.handler.error(context, 'compute.nova01', 'some_event', dict(), dict())
        self.notifier.info.assert_called_once()

        self.notifier.error.assert_not_called()
        self.notifier.critical.assert_not_called()

    def test_notifications_are_sent_to_critical_queue_if_above_threshold(self):
        context = {
            notification.NotificationMessage.RETRY_COUNTER: 3
        }

        event_handler = mock.Mock()
        event_handler.handle_events.side_effect = Exception()

        self.handler.add_event_handler(event_handler)

        self.handler.info(context, 'compute.nova01', 'some_event', dict(), dict())
        self.notifier.critical.assert_called_once()

        self.notifier.info.assert_not_called()
        self.notifier.error.assert_not_called()

    def test_unrelated_notifications_are_not_handled_in_error_queue(self):
        self.handler.error(dict(), 'compute.nova01', 'some_event', dict(), dict())
        self.notifier.info.assert_not_called()
        self.notifier.error.assert_not_called()
        self.notifier.critical.assert_not_called()
