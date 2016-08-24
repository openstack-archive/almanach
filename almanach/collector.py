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

import kombu

from almanach.adapters import bus_adapter
from almanach.adapters import database_adapter
from almanach.adapters import retry_adapter
from almanach import config
from almanach.core import controller


class AlmanachCollector(object):
    def __init__(self):
        self._controller = controller.Controller(database_adapter.DatabaseAdapter())
        _connection = kombu.Connection(config.rabbitmq_url(), heartbeat=540)
        retry_adapter_instance = retry_adapter.RetryAdapter(_connection)
        self._busAdapter = bus_adapter.BusAdapter(self._controller, _connection,
                                                  retry_adapter_instance)

    def run(self):
        logging.info("Listening for incoming events")
        self._busAdapter.run()
