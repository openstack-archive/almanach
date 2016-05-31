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

    def test_volume_delete(self):
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

        volume_delete_query = "{url}/volume/{volume_id}"
        delete_data = {'date': '2016-01-01T18:50:00Z'}
        response = self.almanachHelper.delete(url=volume_delete_query, data=delete_data, volume_id=volume_id)
        assert_that(response.status_code, equal_to(202))

        list_query = "{url}/project/{project}/volumes?start={start}&end={end}"
        response = self.almanachHelper.get(url=list_query, project=project_id,
                                           start="2016-01-01 18:49:00.000", end="2016-01-01 18:51:00.000")

        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_item({'entity_id': volume_id,
                                               'attached_to': create_data['attached_to'],
                                               'end': '2016-01-01 18:50:00+00:00',
                                               'name': create_data['volume_name'],
                                               'entity_type': 'volume',
                                               'last_event': '2016-01-01 18:50:00+00:00',
                                               'volume_type': messages.DEFAULT_VOLUME_TYPE,
                                               'start': '2016-01-01 18:30:00+00:00',
                                               'project_id': project_id,
                                               'size': create_data['size']}))

    def test_volume_delete_bad_date_format(self):
        volume_delete_query = "{url}/volume/{volume_id}"
        delete_data = {'date': 'A_BAD_DATE'}

        response = self.almanachHelper.delete(url=volume_delete_query, data=delete_data, volume_id="my_test_volume_id")
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                'error',
                'The provided date has an invalid format. Format should be of yyyy-mm-ddThh:mm:ss.msZ, '
                'ex: 2015-01-31T18:24:34.1523Z'
        ))

    def test_volume_delete_missing_param(self):
        instance_delete_query = "{url}/volume/{volume_id}"

        response = self.almanachHelper.delete(url=instance_delete_query, data=dict(), volume_id="my_test_volume_id")
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                "error",
                "The 'date' param is mandatory for the request you have made."
        ))
