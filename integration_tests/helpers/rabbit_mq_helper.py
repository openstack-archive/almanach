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

import os

from kombu import BrokerConnection
from kombu import Exchange
from kombu.pools import producers
from kombu.common import maybe_declare


class RabbitMqHelper(object):
    def __init__(self):
        is_container = True if os.environ.get('TEST_CONTAINER') else False
        hostname = "messaging" if is_container else "127.0.0.1"
        amqp_url = "amqp://guest:guest@{url}:{port}".format(url=hostname, port=5672)
        self.task_exchange = Exchange("almanach.info", type="topic")
        self.connection = BrokerConnection(amqp_url)

    def push(self, message):
        with producers[self.connection].acquire(block=True) as producer:
            maybe_declare(self.task_exchange, producer.channel)
            producer.publish(message, routing_key="almanach.info")
