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

import kombu

from oslo_log import log

LOG = log.getLogger(__name__)


class RetryAdapter(object):
    def __init__(self, config, connection):
        self.config = config
        self.connection = connection

        retry_exchange = self._configure_retry_exchanges(self.connection)
        dead_exchange = self._configure_dead_exchange(self.connection)

        self._retry_producer = kombu.Producer(self.connection, exchange=retry_exchange)
        self._dead_producer = kombu.Producer(self.connection, exchange=dead_exchange)

    def publish_to_dead_letter(self, message):
        death_count = self._rejected_count(message)
        LOG.info('Message die %d times', death_count)

        if death_count < self.config.collector.max_retries:
            LOG.info('Publishing message to retry queue')
            self._publish_message(self._retry_producer, message)
        else:
            LOG.info('Publishing message to dead letter queue')
            self._publish_message(self._dead_producer, message)

    def _configure_retry_exchanges(self, connection):
        def declare_queues():
            channel = connection.channel()

            retry_exchange = kombu.Exchange(
                name=self.config.collector.retry_exchange,
                type='direct',
                channel=channel)

            retry_queue = kombu.Queue(
                name=self.config.collector.retry_queue,
                exchange=retry_exchange,
                routing_key=self.config.collector.routing_key,
                queue_arguments=self._get_queue_arguments(),
                channel=channel)

            main_exchange = kombu.Exchange(
                    name=self.config.collector.retry_return_exchange,
                    type='direct',
                    channel=channel)

            main_queue = kombu.Queue(
                name=self.config.collector.queue,
                exchange=main_exchange,
                durable=False,
                routing_key=self.config.collector.routing_key,
                channel=channel)

            retry_queue.declare()
            main_queue.declare()

            return retry_exchange

        def error_callback(exception, interval):
            LOG.error('Failed to declare queues and exchanges, retrying in %d seconds. %r', interval, exception)

        declare_queues = connection.ensure(connection, declare_queues, errback=error_callback,
                                           interval_start=0, interval_step=5, interval_max=30)
        return declare_queues()

    def _configure_dead_exchange(self, connection):
        def declare_dead_queue():
            channel = connection.channel()
            dead_exchange = kombu.Exchange(
                name=self.config.collector.dead_exchange,
                type='direct',
                channel=channel)

            dead_queue = kombu.Queue(
                name=self.config.collector.dead_queue,
                routing_key=self.config.collector.routing_key,
                exchange=dead_exchange,
                channel=channel)

            dead_queue.declare()

            return dead_exchange

        def error_callback(exception, interval):
            LOG.error('Failed to declare dead queue and exchange, retrying in %d seconds. %r',
                      interval, exception)

        declare_dead_queue = connection.ensure(connection, declare_dead_queue, errback=error_callback,
                                               interval_start=0, interval_step=5, interval_max=30)
        return declare_dead_queue()

    def _get_queue_arguments(self):
        return {
            "x-message-ttl": self.config.collector.retry_ttl * 1000,
            "x-dead-letter-exchange": self.config.collector.retry_return_exchange,
            "x-dead-letter-routing-key": self.config.collector.routing_key,
        }

    def _rejected_count(self, message):
        if 'x-death' in message.headers:
            return len(message.headers['x-death'])
        return 0

    def _publish_message(self, producer, message):
        publish = self.connection.ensure(producer, producer.publish, errback=self._error_callback,
                                         interval_start=0, interval_step=5, interval_max=30)
        publish(message.body,
                routing_key=message.delivery_info['routing_key'],
                headers=message.headers,
                content_type=message.content_type,
                content_encoding=message.content_encoding)

    def _error_callback(self, exception, interval):
        LOG.error('Failed to publish message to dead letter queue, retrying in %d seconds. %r',
                  interval, exception)
