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
import oslo_messaging

LOG = logging.getLogger(__name__)


class MessagingFactory(object):

    def __init__(self, config):
        self.config = config

    def get_listeners(self, handler):
        listeners = []
        targets = [
            oslo_messaging.Target(topic=self.config.collector.topic),
        ]

        for url in self.config.collector.transport_url:
            LOG.debug('Creating listener for %s', url)
            transport = self._get_transport(url)
            listeners.append(oslo_messaging.get_notification_listener(transport=transport,
                                                                      targets=targets,
                                                                      endpoints=[handler],
                                                                      executor='threading'))
        return listeners

    def get_notifier(self):
        transport = self._get_transport(self.config.collector.transport_url[0])
        return oslo_messaging.Notifier(transport, publisher_id='almanach.collector',
                                       topics=[self.config.collector.topic], driver='messagingv2')

    def _get_transport(self, url):
        return oslo_messaging.get_notification_transport(self.config, url=url)
