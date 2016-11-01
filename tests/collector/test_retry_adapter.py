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

from almanach.collector import retry_adapter
from tests import base


class BusAdapterTest(base.BaseTestCase):

    def setUp(self):
        super(BusAdapterTest, self).setUp()
        self.connection = mock.Mock()
        self.retry_producer = mock.Mock()
        self.dead_producer = mock.Mock()
        self.retry_adapter = retry_adapter.RetryAdapter(self.config, self.connection,
                                                        self.retry_producer, self.dead_producer)

    def test_message_is_published_to_retry_queue(self):
        message = mock.Mock(headers=dict())
        message.delivery_info = dict(routing_key='test')

        self.retry_adapter.publish_to_dead_letter(message)
        self.connection.ensure.assert_called_with(self.retry_producer, self.retry_producer.publish,
                                                  errback=self.retry_adapter._error_callback,
                                                  interval_max=30, interval_start=0, interval_step=5)

    def test_message_is_published_to_dead_queue(self):
        message = mock.Mock(headers={'x-death': [0, 1, 2, 3]})
        message.delivery_info = dict(routing_key='test')

        self.retry_adapter.publish_to_dead_letter(message)
        self.assertEqual(self.connection.ensure.call_count, 3)

        self.connection.ensure.assert_called_with(self.dead_producer, self.dead_producer.publish,
                                                  errback=self.retry_adapter._error_callback,
                                                  interval_max=30, interval_start=0, interval_step=5)
