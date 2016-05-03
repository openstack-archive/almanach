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

import argparse
import sys
import logging
import logging.config as logging_config

from almanach import config
from almanach.api import AlmanachApi
from almanach.collector import AlmanachCollector


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("service", help="Service to execute: 'api' or 'collector'", choices=["api", "collector"])
    parser.add_argument("config_file", help="Config file path")
    parser.add_argument("--logging", help="Logger configuration")
    parser.add_argument("--port", help="API HTTP port (default is 8000)", default=8000)
    parser.add_argument("--host", help="API hostname to listen on (default is 127.0.0.1)", default="127.0.0.1")
    args = parser.parse_args()

    config.read(args.config_file)

    if args.logging:
        print("Loading logger configuration from {0}".format(args.logging))
        logging_config.fileConfig(args.logging, disable_existing_loggers=False)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logging.debug("Logging to stdout")

    if args.service == "api":
        almanach_api = AlmanachApi()
        almanach_api.run(host=args.host, port=args.port)
    else:
        almanach_collector = AlmanachCollector()
        almanach_collector.run()


if __name__ == "__main__":
    run()
