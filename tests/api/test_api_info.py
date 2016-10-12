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

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_key

from tests.api.base_api import BaseApi


class ApiInfoTest(BaseApi):

    def test_info(self):
        self.controller.should_receive('get_application_info').and_return({
            'info': {'version': '1.0'},
            'database': {'all_entities': 10,
                         'active_entities': 2}
        })

        code, result = self.api_get('/info')

        assert_that(code, equal_to(200))
        assert_that(result, has_key('info'))
        assert_that(result['info']['version'], equal_to('1.0'))
