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

from hamcrest import assert_that, equal_to

from tests.api.base_api import BaseApi


class ApiAuthenticationTest(BaseApi):
    def setUp(self):
        self.prepare()
        self.prepare_with_failed_authentication()

    def test_with_wrong_authentication(self):
        self.controller.should_receive('list_entities').never()
        query_string = {'start': '2014-01-01 00:00:00.0000', 'end': '2014-02-01 00:00:00.0000'}

        code, result = self.api_get(url='/project/TENANT_ID/entities',
                                    query_string=query_string,
                                    headers={'X-Auth-Token': 'wrong token'})

        assert_that(code, equal_to(401))
