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

from flexmock import flexmock
from kombu import Connection
from kombu.tests import mocks
from kombu.transport import pyamqp

from almanach.collector import retry_adapter
from tests import base


class BusAdapterTest(base.BaseTestCase):

    def setUp(self):
        super(BusAdapterTest, self).setUp()
        self.setup_connection_mock()
        self.retry_adapter = retry_adapter.RetryAdapter(self.config, self.connection)

    def setup_connection_mock(self):
        mocks.Transport.recoverable_connection_errors = pyamqp.Transport.recoverable_connection_errors
        self.connection = flexmock(Connection(transport=mocks.Transport))
        self.channel_mock = flexmock(self.connection.default_channel)
        self.connection.should_receive('channel').and_return(self.channel_mock)

    def test_declare_retry_exchanges_retries_if_it_fails(self):
        connection = flexmock(Connection(transport=mocks.Transport))
        connection.should_receive('_establish_connection').times(3)\
            .and_raise(IOError)\
            .and_raise(IOError)\
            .and_return(connection.transport.establish_connection())

        self.retry_adapter = retry_adapter.RetryAdapter(self.config, connection)

    def test_publish_to_retry_queue_happy_path(self):
        message = self.build_message()

        self.expect_publish_with(message, 'almanach.retry').once()
        self.retry_adapter.publish_to_dead_letter(message)

    def test_publish_to_retry_queue_retries_if_it_fails(self):
        message = self.build_message()

        self.expect_publish_with(message, 'almanach.retry').times(4)\
            .and_raise(IOError)\
            .and_raise(IOError)\
            .and_raise(IOError)\
            .and_return(message)

        self.retry_adapter.publish_to_dead_letter(message)

    def build_message(self, headers=dict()):
        message = MyObject()
        message.headers = headers
        message.body = b'Now that the worst is behind you, it\'s time we get you back. - Mr. Robot'
        message.delivery_info = {'routing_key': 42}
        message.content_type = 'xml/rapture'
        message.content_encoding = 'iso8859-1'
        return message

    def test_publish_to_dead_letter_messages_retried_more_than_twice(self):
        message = self.build_message(headers={'x-death': [0, 1, 2, 3]})

        self.expect_publish_with(message, 'almanach.dead').once()

        self.retry_adapter.publish_to_dead_letter(message)

    def expect_publish_with(self, message, exchange):
        expected_message = {'body': message.body,
                            'priority': 0,
                            'content_encoding': message.content_encoding,
                            'content_type': message.content_type,
                            'headers': message.headers,
                            'properties': {'delivery_mode': 2}}

        return self.channel_mock.should_receive('basic_publish')\
            .with_args(expected_message, exchange=exchange, routing_key=message.delivery_info['routing_key'],
                       mandatory=False, immediate=False)


class MyObject(object):
    headers = None
    body = None
    delivery_info = None
    content_type = None
    content_encoding = None
