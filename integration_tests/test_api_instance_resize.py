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
from hamcrest import assert_that, equal_to, has_item, has_entry

from base_api_testcase import BaseApiTestCase


class ApiInstanceDelete(BaseApiTestCase):

    def test_instance_resize(self):
        instance_create_query = "{url}/project/{project}/instance"
        project_id = "my_test_project_id"
        instance_id = str(uuid4())
        create_data = {'id': instance_id,
                       'created_at': '2016-01-01T18:30:00Z',
                       'name': 'integration_test_instance_FlavorA',
                       'flavor': 'FlavorA',
                       'os_type': 'Linux',
                       'os_distro': 'Ubuntu',
                       'os_version': '14.04'}

        response = self.almanachHelper.post(url=instance_create_query, data=create_data, project=project_id)
        assert_that(response.status_code, equal_to(201))

        instance_resize_query = "{url}/instance/{instance_id}/resize"
        resize_data = {'date': '2016-01-01T18:40:00Z',
                       'flavor': 'FlavorC'}

        response = self.almanachHelper.put(url=instance_resize_query, data=resize_data, instance_id=instance_id)
        assert_that(response.status_code, equal_to(200))

        list_query = "{url}/project/{project}/instances?start={start}&end={end}"
        response = self.almanachHelper.get(url=list_query,
                                           project=project_id,
                                           start="2016-01-01 18:39:00.000",
                                           end="2016-01-01 18:41:00.000")

        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_item({'entity_id': instance_id,
                                               'end': None,
                                               'entity_type': 'instance',
                                               'flavor': resize_data['flavor'],
                                               'last_event': '2016-01-01 18:40:00+00:00',
                                               'name': create_data['name'],
                                               'os': {
                                                   'distro': create_data['os_distro'],
                                                   'os_type': create_data['os_type'],
                                                   'version': create_data['os_version']
                                               },
                                               'project_id': project_id,
                                               'start': '2016-01-01 18:40:00+00:00',
                                               'metadata': {}}))

    def test_instance_resize_bad_date_format(self):
        instance_resize_query = "{url}/instance/{instance_id}/resize"
        resize_data = {'date': 'A_BAD_DATE',
                       'flavor': 'FlavorC'}

        response = self.almanachHelper.put(url=instance_resize_query, data=resize_data, instance_id="my_instance_id")
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                'error',
                'The provided date has an invalid format. Format should be of yyyy-mm-ddThh:mm:ss.msZ, '
                'ex: 2015-01-31T18:24:34.1523Z'
        ))

    def test_instance_resize_missing_param(self):
        instance_resize_query = "{url}/instance/{instance_id}/resize"
        resize_data = {'flavor': 'FlavorC'}

        response = self.almanachHelper.put(url=instance_resize_query, data=resize_data, instance_id="my_instance_id")
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                "error",
                "The 'date' param is mandatory for the request you have made."
        ))
