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

from almanach.tests.unit.api.v1 import base_api


class TestApiInfo(base_api.BaseApi):

    def test_info(self):
        info = {'info': {'version': '1.0'}, 'database': {'all_entities': 10, 'active_entities': 2}}
        self.app_ctl.get_application_info.return_value = info

        code, result = self.api_get('/info')

        self.app_ctl.get_application_info.assert_called_once()
        self.assertEqual(code, 200)
        self.assertIn('info', result)
        self.assertEqual(result['info']['version'], '1.0')
