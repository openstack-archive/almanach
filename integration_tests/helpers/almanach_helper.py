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
import os
import requests


class AlmanachHelper(object):
    x_auth_token = 'secret'

    def __init__(self):
        is_container = True if os.environ.get('TEST_CONTAINER') else False
        port = 8000 if is_container else 80
        hostname = "api" if is_container else "127.0.0.1"
        self.base_url = "http://{url}:{port}".format(url=hostname, port=port)

    def get_entities(self, tenant_id, start):
        url = "{url}/project/{project}/entities?start={start}".format(
            url=self.base_url, project=tenant_id, start=start
        )

        response = requests.get(url, headers=self._get_query_headers())
        return response.json()

    def get(self, url, headers=None, **params):
        return requests.get(
            url.format(url=self.base_url, **params),
            headers=headers if headers else self._get_query_headers()
        )

    def head(self, url, headers=None, **params):
        return requests.head(
            url.format(url=self.base_url, **params),
            headers=headers if headers else self._get_query_headers()
        )

    def post(self, url, data, **params):
        return requests.post(
            url.format(url=self.base_url, **params),
            data=json.dumps(data),
            headers=self._get_query_headers()
        )

    def put(self, url, data, **params):
        return requests.put(
            url.format(url=self.base_url, **params),
            data=json.dumps(data),
            headers=self._get_query_headers()
        )

    def delete(self, url, data, **params):
        return requests.delete(
            url.format(url=self.base_url, **params),
            data=json.dumps(data),
            headers=self._get_query_headers()
        )

    def _get_query_headers(self):
        return {
            'X-Auth-Token': self.x_auth_token,
            'Accept': 'application/json'
        }
