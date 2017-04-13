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

import oslo_messaging

from almanach.collector import service

from almanach.tests.unit import base


class TestService(base.BaseTestCase):

    def setUp(self):
        super(TestService, self).setUp()
        self.listener = mock.Mock()
        self.listeners = [self.listener]
        self.service = service.CollectorService(self.listeners, self.config.collector.thread_pool_size)

    def test_start_when_listener_started_successfully(self):
        self.service.start()
        self.listeners[0].start.assert_called_once_with(override_pool_size=self.config.collector.thread_pool_size)
        self.assertTrue(self.service.started)

    def test_start_when_listener_failed_to_start(self):
        self.listener.start.side_effect = oslo_messaging.exceptions.MessagingException('Some Error')
        self.assertRaises(oslo_messaging.exceptions.MessagingException, self.service.start)
        self.assertFalse(self.service.started)

    def test_stop_when_service_started_successfully(self):
        self.service.started = True
        self.service.stop()
        self.listener.stop.assert_called_once()

    def test_stop_when_service_failed_to_start(self):
        self.service.stop()
        self.listener.stop.assert_not_called()
