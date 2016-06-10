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

import json
import logging
import kombu

from kombu.mixins import ConsumerMixin
from almanach import config
from almanach.adapters.instance_bus_adapter import InstanceBusAdapter
from almanach.adapters.volume_bus_adapter import VolumeBusAdapter


class BusAdapter(ConsumerMixin):

    def __init__(self, controller, connection, retry_adapter):
        super(BusAdapter, self).__init__()
        self.controller = controller
        self.connection = connection
        self.retry_adapter = retry_adapter

    def on_message(self, notification, message):
        try:
            self._process_notification(notification)
        except Exception as e:
            logging.warning("Sending notification to retry letter exchange {0}".format(json.dumps(notification)))
            logging.exception(e.message)
            self.retry_adapter.publish_to_dead_letter(message)
        message.ack()

    def _process_notification(self, notification):
        if isinstance(notification, basestring):
            notification = json.loads(notification)

        event_type = notification.get("event_type")
        logging.info("Received event: '{0}'".format(event_type))
        InstanceBusAdapter(self.controller).handle_events(event_type, notification)
        VolumeBusAdapter(self.controller).handle_events(event_type, notification)

    def get_consumers(self, consumer, channel):
        queue = kombu.Queue(config.rabbitmq_queue(), routing_key=config.rabbitmq_routing_key())
        return [consumer(
            [queue],
            callbacks=[self.on_message],
            auto_declare=False)]

    def run(self, _tokens=1):
        try:
            super(BusAdapter, self).run(_tokens)
        except KeyboardInterrupt:
            pass
