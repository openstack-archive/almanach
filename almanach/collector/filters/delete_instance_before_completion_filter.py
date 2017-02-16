# Copyright 2017 Internap.
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

from almanach.collector.filters import base_filter
from almanach.core.helpers import date_helper

LOG = logging.getLogger(__name__)


class DeleteInstanceBeforeCompletionFilter(base_filter.BaseFilter):

    def __init__(self, config):
        self.config = config

    def ignore_notification(self, notification):
        delta = self.config.entities.instance_existence_threshold

        if self._has_been_retried(notification) \
                and self._is_instance_deleted(notification) \
                and self._was_never_created_successfully(notification, delta):
            LOG.info('Instance %s was never created successfully during %d seconds',
                     notification.payload.get('instance_id'),
                     delta)
            return True
        return False

    @staticmethod
    def _is_instance_deleted(notification):
        return notification.payload.get('state') == 'deleted'

    def _has_been_retried(self, notification):
        return notification.get_retry_counter() >= self.config.collector.min_retries

    @staticmethod
    def _was_never_created_successfully(notification, delta):
        creation_date = date_helper.DateHelper().parse(notification.payload.get('created_at'))
        deletion_date = date_helper.DateHelper().parse(notification.payload.get('deleted_at'))
        return date_helper.DateHelper().is_within_range(creation_date, deletion_date, delta)
