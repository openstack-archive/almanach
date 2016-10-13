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

from flask import Flask
from oslo_log import log

from almanach.api import auth_adapter
from almanach.api.v1 import routes
from almanach.core import controller
from almanach.core import opts
from almanach.storage import storage_driver

LOG = log.getLogger(__name__)

app = Flask('almanach')
app.register_blueprint(routes.api)


def main():
    try:
        opts.CONF(sys.argv[1:])
        config = opts.CONF

        database_driver = storage_driver.StorageDriver(config).get_database_driver()
        database_driver.connect()

        routes.controller = controller.Controller(config, database_driver)
        routes.auth_adapter = auth_adapter.AuthenticationAdapter(config).get_authentication_adapter()

        LOG.info('Listening on %s:%d', config.api.bind_ip, config.api.bind_port)
        app.run(host=config.api.bind_ip, port=config.api.bind_port)
    except Exception as e:
        LOG.exception(e)
        sys.exit(100)

if __name__ == '__main__':
    main()
