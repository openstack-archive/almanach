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
from tests import base


class MessagingFactoryTest(base.BaseTestCase):

    def setUp(self):
        super(MessagingFactoryTest, self).setUp()
        self.factory = messaging.MessagingFactory(self.config)

    def test_get_listener(self):
        self.assertIsNotNone(self.factory.get_listener(mock.Mock()))

    def test_get_notifier(self):
        self.assertIsInstance(self.factory.get_notifier(), oslo_messaging.Notifier)
