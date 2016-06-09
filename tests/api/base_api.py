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

import json
import flask

from unittest import TestCase
from datetime import datetime
from flexmock import flexmock, flexmock_teardown

from almanach import config
from almanach.adapters import api_route_v1 as api_route
from almanach.common.exceptions.authentication_failure_exception import AuthenticationFailureException


class BaseApi(TestCase):
    def setUp(self):
        self.prepare()
        self.prepare_with_successful_authentication()

    def tearDown(self):
        flexmock_teardown()

    @staticmethod
    def having_config(key, value):
        (flexmock(config)
         .should_receive(key)
         .and_return(value))

    def prepare(self):
        self.controller = flexmock()
        self.auth_adapter = flexmock()
        api_route.controller = self.controller
        api_route.auth_adapter = self.auth_adapter

        self.app = flask.Flask("almanach")
        self.app.register_blueprint(api_route.api)

    def prepare_with_successful_authentication(self):
        self.having_config('auth_private_key', 'some token value')
        self.auth_adapter.should_receive("validate").and_return(True)

    def prepare_with_failed_authentication(self):
        self.having_config('auth_private_key', 'some token value')
        self.auth_adapter.should_receive("validate").and_raise(AuthenticationFailureException("Wrong credentials"))

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


def a_date_matching(date_string):
    return DateMatcher(datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f"))
