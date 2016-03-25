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

import logging
import sys

from kombu import Connection

from almanach import log_bootstrap
from almanach import config
from almanach.adapters.bus_adapter import BusAdapter
from almanach.adapters.database_adapter import DatabaseAdapter
from almanach.adapters.retry_adapter import RetryAdapter
from almanach.core.controller import Controller


class AlmanachCollector(object):
    def __init__(self):
        log_bootstrap.configure()
        config.read(sys.argv)
        self._controller = Controller(DatabaseAdapter())
        _connection = Connection(config.rabbitmq_url(), heartbeat=540)
        retry_adapter = RetryAdapter(_connection)

        self._busAdapter = BusAdapter(self._controller, _connection, retry_adapter)

    def run(self):
        logging.info("starting bus adapter")
        self._busAdapter.run()
        logging.info("shutting down")


def run():
    almanach_collector = AlmanachCollector()
    almanach_collector.run()


if __name__ == "__main__":
    run()
