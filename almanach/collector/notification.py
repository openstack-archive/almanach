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

from oslo_log import log as logging
import time

LOG = logging.getLogger(__name__)


class NotificationMessage(object):
    RETRY_COUNTER = 'retry_count'

    def __init__(self, event_type, context, payload, metadata):
        self.event_type = event_type
        self.context = context
        self.payload = payload
        self.metadata = metadata

    def increment_retry_count(self):
        if self.RETRY_COUNTER not in self.context:
            self.context[self.RETRY_COUNTER] = 1
        else:
            self.context[self.RETRY_COUNTER] += 1

    def get_retry_counter(self):
        if self.RETRY_COUNTER not in self.context:
            return 0
        return self.context[self.RETRY_COUNTER]


class NotificationHandler(object):

    def __init__(self, config, messaging):
        self.config = config
        self.messaging = messaging
        self.handlers = []

    def add_event_handler(self, handler):
        self.handlers.append(handler)

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        LOG.info('Received event "%s" from "%s" on info queue', event_type, publisher_id)
        notification = NotificationMessage(event_type, ctxt, payload, metadata)

        try:
            for handler in self.handlers:
                handler.handle_events(notification)
        except Exception as e:
            LOG.warning('Send notification "%s" to error queue', notification.metadata.get('message_id'))
            LOG.warning('Notification event_type: %s', notification.event_type)
            LOG.warning('Notification context: %s', notification.context)
            LOG.warning('Notification payload: %s', notification.payload)
            LOG.warning('Notification metadata: %s', notification.metadata)
            LOG.exception(e)
            self._retry_notification(notification)

    def error(self, ctxt, publisher_id, event_type, payload, metadata):
        LOG.warning('Received event "%s" from "%s" on error queue', event_type, publisher_id)
        notification = NotificationMessage(event_type, ctxt, payload, metadata)
        time.sleep(self.config.collector.retry_delay)
        self._retry_notification(notification)

    def _retry_notification(self, notification):
        notification.increment_retry_count()
        notifier = self.messaging.get_notifier()

        if notification.get_retry_counter() > self.config.collector.max_retries:
            LOG.critical('Send notification "%s" to critical queue', notification.metadata.get('message_id'))
            notifier.critical(notification.context, notification.event_type, notification.payload)
        else:
            notifier.error(notification.context, notification.event_type, notification.payload)
