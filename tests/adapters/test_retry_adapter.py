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

import unittest

from kombu import Connection
from kombu.tests import mocks
from kombu.transport import pyamqp
from flexmock import flexmock, flexmock_teardown

from almanach import config
from almanach.adapters.retry_adapter import RetryAdapter


class BusAdapterTest(unittest.TestCase):

    def setUp(self):
        self.setup_connection_mock()
        self.setup_config_mock()

        self.retry_adapter = RetryAdapter(self.connection)

    def tearDown(self):
        flexmock_teardown()

    def setup_connection_mock(self):
        mocks.Transport.recoverable_connection_errors = pyamqp.Transport.recoverable_connection_errors
        self.connection = flexmock(Connection(transport=mocks.Transport))
        self.channel_mock = flexmock(self.connection.default_channel)
        self.connection.should_receive('channel').and_return(self.channel_mock)

    def setup_config_mock(self):
        self.config_mock = flexmock(config)
        self.config_mock.should_receive('rabbitmq_time_to_live').and_return(10)
        self.config_mock.should_receive('rabbitmq_routing_key').and_return('almanach.info')
        self.config_mock.should_receive('rabbitmq_retry_queue').and_return('almanach.retry')
        self.config_mock.should_receive('rabbitmq_dead_queue').and_return('almanach.dead')
        self.config_mock.should_receive('rabbitmq_queue').and_return('almanach.info')
        self.config_mock.should_receive('rabbitmq_retry_return_exchange').and_return('almanach')
        self.config_mock.should_receive('rabbitmq_retry_exchange').and_return('almanach.retry')
        self.config_mock.should_receive('rabbitmq_dead_exchange').and_return('almanach.dead')

    def test_declare_retry_exchanges_retries_if_it_fails(self):
        connection = flexmock(Connection(transport=mocks.Transport))
        connection.should_receive('_establish_connection').times(3)\
            .and_raise(IOError)\
            .and_raise(IOError)\
            .and_return(connection.transport.establish_connection())

        self.retry_adapter = RetryAdapter(connection)

    def test_publish_to_retry_queue_happy_path(self):
        message = MyObject
        message.headers = []
        message.body = 'omnomnom'
        message.delivery_info = {'routing_key': 42}
        message.content_type = 'xml/rapture'
        message.content_encoding = 'iso8859-1'

        self.config_mock.should_receive('rabbitmq_retry').and_return(1)
        self.expect_publish_with(message, 'almanach.retry').once()

        self.retry_adapter.publish_to_dead_letter(message)

    def test_publish_to_retry_queue_retries_if_it_fails(self):
        message = MyObject
        message.headers = {}
        message.body = 'omnomnom'
        message.delivery_info = {'routing_key': 42}
        message.content_type = 'xml/rapture'
        message.content_encoding = 'iso8859-1'

        self.config_mock.should_receive('rabbitmq_retry').and_return(2)
        self.expect_publish_with(message, 'almanach.retry').times(4)\
            .and_raise(IOError)\
            .and_raise(IOError)\
            .and_raise(IOError)\
            .and_return(message)

        self.retry_adapter.publish_to_dead_letter(message)

    def test_publish_to_dead_letter_messages_retried_more_than_twice(self):
        message = MyObject
        message.headers = {'x-death': [0, 1, 2, 3]}
        message.body = 'omnomnom'
        message.delivery_info = {'routing_key': ''}
        message.content_type = 'xml/rapture'
        message.content_encoding = 'iso8859-1'

        self.config_mock.should_receive('rabbitmq_retry').and_return(2)
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
    pass
