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
from base_api_testcase import BaseApiTestCase


class ApiAuthenticationTest(BaseApiTestCase):

    def test_list_entities_unauthorized(self):
        list_query = "{url}/project/{project}/instances?start={start}&end={end}"
        response = self.almanachHelper.get(url=list_query, headers={'Accept': 'application/json'},
                                           project="e455d65807cb4796bd72abecdc8a76ba",
                                           start="2014-02-28 18:50:00.000", end="2014-03-21 22:00:00.000")
        assert_that(response.status_code, equal_to(401))
