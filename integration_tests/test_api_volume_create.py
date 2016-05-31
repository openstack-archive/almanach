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

from uuid import uuid4
from hamcrest import equal_to, assert_that, has_entry, has_item

from base_api_volume_testcase import BaseApiVolumeTestCase
from builders import messages


class ApiVolumeTest(BaseApiVolumeTestCase):

    def test_volume_create(self):
        volume_create_query = "{url}/project/{project}/volume"
        project_id = "my_test_project_id"
        volume_id = str(uuid4())
        data = {'volume_id': volume_id,
                'attached_to': [],
                'volume_name': messages.DEFAULT_VOLUME_NAME,
                'volume_type': messages.DEFAULT_VOLUME_TYPE,
                'start': '2016-01-01T18:30:00Z',
                'size': 100}

        response = self.almanachHelper.post(url=volume_create_query, data=data, project=project_id)
        assert_that(response.status_code, equal_to(201))

        list_query = "{url}/project/{project}/volumes?start={start}&end={end}"
        response = self.almanachHelper.get(url=list_query,
                                           project=project_id,
                                           start="2016-01-01 18:29:00.000", end="2016-01-01 18:31:00.000")

        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_item({'entity_id': volume_id,
                                               'attached_to': data['attached_to'],
                                               'end': None,
                                               'name': data['volume_name'],
                                               'entity_type': 'volume',
                                               'last_event': '2016-01-01 18:30:00+00:00',
                                               'volume_type': messages.DEFAULT_VOLUME_TYPE,
                                               'start': '2016-01-01 18:30:00+00:00',
                                               'project_id': project_id,
                                               'size': data['size']}))

    def test_volume_create_bad_date_format(self):
        volume_create_query = "{url}/project/{project}/volume"
        project_id = "my_test_project_id"
        volume_id = str(uuid4())
        data = {'volume_id': volume_id,
                'attached_to': [],
                'volume_name': messages.DEFAULT_VOLUME_NAME,
                'volume_type': messages.DEFAULT_VOLUME_TYPE,
                'start': 'BAD_DATE_FORMAT',
                'size': 100}

        response = self.almanachHelper.post(url=volume_create_query, data=data, project=project_id)

        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                'error',
                'The provided date has an invalid format. Format should be of yyyy-mm-ddThh:mm:ss.msZ, '
                'ex: 2015-01-31T18:24:34.1523Z'
        ))

    def test_volume_create_missing_param(self):
        volume_create_query = "{url}/project/{project}/volume"
        project_id = "my_test_project_id"
        volume_id = str(uuid4())
        data = {'volume_id': volume_id,
                'attached_to': [],
                'volume_name': messages.DEFAULT_VOLUME_NAME,
                'volume_type': messages.DEFAULT_VOLUME_TYPE,
                'size': 100}

        response = self.almanachHelper.post(url=volume_create_query, data=data, project=project_id)

        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                "error",
                "The 'start' param is mandatory for the request you have made."
        ))
