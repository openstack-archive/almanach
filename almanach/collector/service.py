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
from oslo_service import service

from almanach.collector.filters import delete_instance_before_completion_filter
from almanach.collector.filters import errored_instance_filter
from almanach.collector.handlers import instance_handler
from almanach.collector.handlers import volume_handler
from almanach.collector.handlers import volume_type_handler
from almanach.collector import messaging
from almanach.collector import notification

LOG = logging.getLogger(__name__)


class CollectorService(service.ServiceBase):

    def __init__(self, listeners):
        super(CollectorService, self).__init__()
        self.listeners = listeners

    def start(self):
        LOG.info('Starting collector listeners...')
        for listener in self.listeners:
            listener.start()

    def wait(self):
        LOG.info('Waiting...')

    def stop(self):
        LOG.info('Graceful shutdown of the collector service...')
        for listener in self.listeners:
            listener.stop()

    def reset(self):
        pass


class ServiceFactory(object):

    def __init__(self, config, core_factory):
        self.config = config
        self.core_factory = core_factory

    def get_service(self):
        messaging_factory = messaging.MessagingFactory(self.config)

        notification_handler = notification.NotificationHandler(self.config, messaging_factory)
        notification_handler.add_event_handler(self.get_instance_handler())
        notification_handler.add_event_handler(self.get_volume_handler())
        notification_handler.add_event_handler(self.get_volume_type_handler())

        listeners = messaging_factory.get_listeners(notification_handler)
        return CollectorService(listeners)

    def get_instance_handler(self):
        return instance_handler.InstanceHandler(
                self.core_factory.get_instance_controller(),
                self.get_on_delete_filters())

    def get_volume_handler(self):
        return volume_handler.VolumeHandler(self.core_factory.get_volume_controller())

    def get_volume_type_handler(self):
        return volume_type_handler.VolumeTypeHandler(self.core_factory.get_volume_type_controller())

    def get_on_delete_filters(self):
        filters = notification.NotificationFilter()
        filters.add(errored_instance_filter.ErroredInstanceFilter())
        filters.add(delete_instance_before_completion_filter.DeleteInstanceBeforeCompletionFilter(self.config))
        return filters
