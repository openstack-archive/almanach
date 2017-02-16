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

import sys

from oslo_log import log as logging
from oslo_service import service

from almanach.collector import service as collector_service
from almanach.core import factory as core_factory
from almanach.core import opts


def main():
    opts.CONF(sys.argv[1:], project=opts.DOMAIN)
    logging.setup(opts.CONF, opts.DOMAIN)
    config = opts.CONF

    service_factory = collector_service.ServiceFactory(config, core_factory.Factory(config))
    launcher = service.launch(config, service_factory.get_service())
    launcher.wait()

if __name__ == '__main__':
    main()
