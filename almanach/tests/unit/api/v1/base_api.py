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

from datetime import datetime
from mock import mock

import flask
from oslo_serialization import jsonutils as json

from almanach.api.v1 import routes
from almanach.tests.unit import base


class BaseApi(base.BaseTestCase):

    def setUp(self):
        super(BaseApi, self).setUp()
        self.prepare()

    def prepare(self):
        self.instance_ctl = mock.Mock()
        self.volume_ctl = mock.Mock()
        self.volume_type_ctl = mock.Mock()
        self.entity_ctl = mock.Mock()
        self.app_ctl = mock.Mock()
        self.auth_adapter = mock.Mock()
        routes.instance_ctl = self.instance_ctl
        routes.volume_ctl = self.volume_ctl
        routes.volume_type_ctl = self.volume_type_ctl
        routes.entity_ctl = self.entity_ctl
        routes.app_ctl = self.app_ctl
        routes.auth_adapter = self.auth_adapter

        self.app = flask.Flask("almanach")
        self.app.register_blueprint(routes.api)

    def api_get(self, url, query_string=None, headers=None, accept='application/json'):
        return self._api_call(url, "get", None, query_string, headers, accept)

    def api_head(self, url, headers):
        return self._api_call(url=url, method="head", headers=headers, accept='application/json')

    def api_post(self, url, data=None, query_string=None, headers=None, accept='application/json'):
        return self._api_call(url, "post", data, query_string, headers, accept)

    def api_put(self, url, data=None, query_string=None, headers=None, accept='application/json'):
        return self._api_call(url, "put", data, query_string, headers, accept)

    def api_delete(self, url, query_string=None, data=None, headers=None, accept='application/json'):
        return self._api_call(url, "delete", data, query_string, headers, accept)

    def _api_call(self, url, method, data=None, query_string=None, headers=None, accept='application/json'):
        with self.app.test_client() as http_client:
            if not headers:
                headers = {}
        headers['Accept'] = accept
        result = getattr(http_client, method)(url, data=json.dumps(data), query_string=query_string, headers=headers)
        return_data = json.loads(result.data) \
            if result.headers.get('Content-Type') == 'application/json' \
            else result.data
        return result.status_code, return_data


class DateMatcher(object):
    def __init__(self, date):
        self.date = date

    def __eq__(self, other):
        return other == self.date

    def __ne__(self, other):
        return not self.__eq__(other)


def a_date_matching(date_string):
    return DateMatcher(datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f"))
