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

from almanach.collector import messaging
from almanach.tests.unit import base


class TestMessagingFactory(base.BaseTestCase):

    def setUp(self):
        super(TestMessagingFactory, self).setUp()
        self.factory = messaging.MessagingFactory(self.config)

    def test_get_listeners_with_one_listener(self):
        self.config.collector.transport_url = ['rabbit://guest:guest@localhost:5672']
        listeners = self.factory.get_listeners(mock.Mock())
        self.assertEqual(1, len(listeners))

    def test_get_listeners_with_multiple_listener(self):
        self.config.collector.transport_url = ['rabbit://guest:guest@localhost:5672',
                                               'rabbit://guest:guest@localhost:5673']
        listeners = self.factory.get_listeners(mock.Mock())
        self.assertEqual(2, len(listeners))

    def test_get_notifier(self):
        self.assertIsInstance(self.factory.get_notifier(), oslo_messaging.Notifier)
