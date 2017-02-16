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

import mock

from almanach.collector import notification

from almanach.tests.unit import base


class TestNotificationFilter(base.BaseTestCase):

    def setUp(self):
        super(TestNotificationFilter, self).setUp()
        self.filter = notification.NotificationFilter()

    def test_when_one_filter_returns_true(self):
        notification = mock.Mock()
        filter1 = mock.Mock()
        filter2 = mock.Mock()

        self.filter.add(filter1)
        self.filter.add(filter2)

        filter1.ignore_notification.return_value = False
        filter2.ignore_notification.return_value = True

        self.assertTrue(self.filter.ignore_notification(notification))

    def test_when_all_filters_returns_false(self):
        notification = mock.Mock()
        filter1 = mock.Mock()
        filter2 = mock.Mock()

        self.filter.add(filter1)
        self.filter.add(filter2)

        filter1.ignore_notification.return_value = False
        filter2.ignore_notification.return_value = False

        self.assertFalse(self.filter.ignore_notification(notification))
