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

    def test_volume_resize(self):
        volume_create_query = "{url}/project/{project}/volume"
        project_id = "my_test_project_id"
        volume_id = str(uuid4())
        create_data = {'volume_id': volume_id,
                       'attached_to': [],
                       'volume_name': messages.DEFAULT_VOLUME_NAME,
                       'volume_type': messages.DEFAULT_VOLUME_TYPE,
                       'start': '2016-01-01T18:30:00Z',
                       'size': 100}

        response = self.almanachHelper.post(url=volume_create_query, data=create_data, project=project_id)
        assert_that(response.status_code, equal_to(201))

        resize_data = {'date': '2016-01-01T18:40:00Z',
                       'size': '150'}

        volume_resize_query = "{url}/volume/{volume_id}/resize"
        response = self.almanachHelper.put(url=volume_resize_query, data=resize_data, volume_id=volume_id)
        assert_that(response.status_code, equal_to(200))

        list_query = "{url}/project/{project}/volumes?start={start}&end={end}"
        response = self.almanachHelper.get(url=list_query,
                                           project=project_id,
                                           start="2016-01-01 18:39:00.000",
                                           end="2016-01-01 18:41:00.000")

        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_item({'entity_id': volume_id,
                                               'attached_to': create_data['attached_to'],
                                               'end': None,
                                               'name': create_data['volume_name'],
                                               'entity_type': 'volume',
                                               'last_event': '2016-01-01 18:40:00+00:00',
                                               'volume_type': messages.DEFAULT_VOLUME_TYPE,
                                               'start': '2016-01-01 18:40:00+00:00',
                                               'project_id': project_id,
                                               'size': resize_data['size']}))

    def test_volume_resize_bad_date_format(self):
        volume_resize_query = "{url}/volume/my_test_volume_id/resize"
        resize_data = {'date': 'A_BAD_DATE',
                       'size': '150'}

        response = self.almanachHelper.put(url=volume_resize_query, data=resize_data)
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                'error',
                'The provided date has an invalid format. Format should be of yyyy-mm-ddThh:mm:ss.msZ, '
                'ex: 2015-01-31T18:24:34.1523Z'
        ))

    def test_volume_resize_missing_param(self):
        volume_resize_query = "{url}/volume/my_test_volume_id/resize"
        resize_data = {'size': '250'}

        response = self.almanachHelper.put(url=volume_resize_query, data=resize_data, instance_id="my_instance_id")
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                "error",
                "The 'date' param is mandatory for the request you have made."
        ))
