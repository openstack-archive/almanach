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

from almanach.collector.filters import errored_instance_filter

from almanach.tests.unit import base
from almanach.tests.unit.builders import notification as builder


class TestErroredInstanceFilter(base.BaseTestCase):

    def setUp(self):
        super(TestErroredInstanceFilter, self).setUp()
        self.filter = errored_instance_filter.ErroredInstanceFilter()

    def test_instance_in_error_deleted(self):
        notification = builder.InstanceNotificationBuilder() \
            .with_event_type('compute.instance.delete.end') \
            .with_payload_value('state', 'error') \
            .build()

        self.assertTrue(self.filter.ignore_notification(notification))

    def test_active_instance_deleted(self):
        notification = builder.InstanceNotificationBuilder() \
            .with_event_type('compute.instance.delete.end') \
            .with_payload_value('state', 'active') \
            .build()

        self.assertFalse(self.filter.ignore_notification(notification))
