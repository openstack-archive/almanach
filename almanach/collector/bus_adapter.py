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
import six

from kombu import mixins
from oslo_log import log
from oslo_serialization import jsonutils

from almanach.collector.handlers import instance_handler
from almanach.collector.handlers import volume_handler

LOG = log.getLogger(__name__)


class BusAdapter(mixins.ConsumerMixin):
    def __init__(self, config, controller, connection, retry_adapter):
        super(BusAdapter, self).__init__()
        self.config = config
        self.controller = controller
        self.connection = connection
        self.retry_adapter = retry_adapter

    def on_message(self, notification, message):
        try:
            self._process_notification(notification)
        except Exception as e:
            LOG.warning('Sending notification to retry letter exchange %s', jsonutils.dumps(notification))
            LOG.exception(e)
            self.retry_adapter.publish_to_dead_letter(message)
        message.ack()

    def _process_notification(self, notification):
        if isinstance(notification, six.string_types):
            notification = jsonutils.loads(notification)

        event_type = notification.get('event_type')
        LOG.info('Received event: %s', event_type)

        instance_handler.InstanceHandler(self.controller).handle_events(event_type, notification)
        volume_handler.VolumeHandler(self.controller).handle_events(event_type, notification)

    def get_consumers(self, consumer, channel):
        queue = kombu.Queue(self.config.collector.queue, routing_key=self.config.collector.routing_key)
        return [consumer(
            [queue],
            callbacks=[self.on_message],
            auto_declare=False)]

    def run(self, _tokens=1):
        try:
            super(BusAdapter, self).run(_tokens)
        except KeyboardInterrupt:
            pass
