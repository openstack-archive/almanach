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
import sys

from almanach.collector import bus_adapter
from almanach.collector import retry_adapter
from almanach.core import controller
from almanach.core import opts
from almanach.storage import storage_driver

LOG = log.getLogger(__name__)


def main():
    try:
        opts.CONF(sys.argv[1:])
        config = opts.CONF

        database_driver = storage_driver.StorageDriver(config).get_database_driver()
        database_driver.connect()

        application_controller = controller.Controller(config, database_driver)
        connection = kombu.Connection(hostname=config.collector.rabbit_host,
                                      port=config.collector.rabbit_port,
                                      userid=config.collector.rabbit_username,
                                      password=config.collector.rabbit_password,
                                      heartbeat=540)
        retry_listener = retry_adapter.RetryAdapter(config, connection)
        bus_listener = bus_adapter.BusAdapter(config, application_controller,
                                              connection, retry_listener)

        LOG.info('Listening for incoming events')
        bus_listener.run()
    except Exception as e:
        LOG.exception(e)
        sys.exit(100)

if __name__ == '__main__':
    main()
