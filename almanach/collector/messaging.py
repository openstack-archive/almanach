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

import oslo_messaging


class MessagingFactory(object):
    def __init__(self, config):
        self.config = config

    def _get_transport(self):
        return oslo_messaging.get_notification_transport(self.config, url=self.config.collector.transport_url)

    def get_listener(self, handler):
        targets = [
            oslo_messaging.Target(topic=self.config.collector.topic),
        ]

        return oslo_messaging.get_notification_listener(self._get_transport(), targets,
                                                        endpoints=[handler])

    def get_notifier(self):
        return oslo_messaging.Notifier(self._get_transport(), publisher_id='almanach.collector',
                                       topic=self.config.collector.topic, driver='messagingv2')
