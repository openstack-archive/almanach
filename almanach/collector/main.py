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

from oslo_log import log
from oslo_service import service
import sys

from almanach.collector import messaging
from almanach.collector import notification
from almanach.collector import service as collector_service
from almanach.core import controller
from almanach.core import opts
from almanach.storage import storage_driver

LOG = log.getLogger(__name__)


def main():
    try:
        opts.CONF(sys.argv[1:])
        config = opts.CONF
        config.debug = True

        database_driver = storage_driver.StorageDriver(config).get_database_driver()
        database_driver.connect()

        messaging_factory = messaging.MessagingFactory(config)

        app_controller = controller.Controller(config, database_driver)
        handler = notification.NotificationHandler(config, app_controller, messaging_factory)

        listener = messaging_factory.get_listener(handler)

        launcher = service.launch(config, collector_service.CollectorService(listener))
        launcher.wait()
    except Exception as e:
        LOG.exception(e)
        sys.exit(100)

if __name__ == '__main__':
    main()
