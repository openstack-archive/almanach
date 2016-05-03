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

from flask import Flask

from almanach.adapters import api_route_v1 as api_route
from almanach.adapters.database_adapter import DatabaseAdapter
from almanach.core.controller import Controller


class AlmanachApi(object):

    def run(self, host, port):
        api_route.controller = Controller(DatabaseAdapter())

        app = Flask("almanach")
        app.register_blueprint(api_route.api)

        return app.run(host=host, port=port)
