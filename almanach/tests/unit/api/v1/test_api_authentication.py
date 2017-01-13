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

from almanach.core import exception
from almanach.tests.unit.api.v1 import base_api


class TestApiAuthentication(base_api.BaseApi):

    def setUp(self):
        super(TestApiAuthentication, self).setUp()
        self.prepare()

    def test_with_wrong_authentication(self):
        self.auth_adapter.validate.side_effect = exception.AuthenticationFailureException('Unauthorized')
        query_string = {'start': '2014-01-01 00:00:00.0000', 'end': '2014-02-01 00:00:00.0000'}

        code, result = self.api_get(url='/project/TENANT_ID/entities',
                                    query_string=query_string,
                                    headers={'X-Auth-Token': 'wrong token'})

        self.entity_ctl.list_entities.assert_not_called()
        self.assertEqual(code, 401)
