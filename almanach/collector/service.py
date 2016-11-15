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

LOG = logging.getLogger(__name__)


class CollectorService(service.ServiceBase):

    def __init__(self, listener):
        self.listener = listener

    def start(self):
        LOG.info('Starting collector service')
        self.listener.start()

    def wait(self):
        pass

    def stop(self):
        LOG.info('Stopping collector service')
        self.listener.stop()

    def reset(self):
        LOG.info('Reloading collector service')
