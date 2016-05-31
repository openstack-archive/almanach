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


class ApiInstanceCreateTest(BaseApiTestCase):

    def test_instance_create(self):
        instance_create_query = "{url}/project/{project}/instance"
        project_id = "my_test_project_id"
        instance_id = str(uuid4())
        data = {'id': instance_id,
                'created_at': '2016-01-01T18:30:00Z',
                'name': 'integration_test_instance_FlavorA',
                'flavor': 'FlavorA',
                'os_type': 'Linux',
                'os_distro': 'Ubuntu',
                'os_version': '14.04'}

        response = self.almanachHelper.post(url=instance_create_query, data=data, project=project_id)
        assert_that(response.status_code, equal_to(201))

        list_query = "{url}/project/{project}/instances?start={start}&end={end}"
        response = self.almanachHelper.get(url=list_query, project=project_id,
                                           start="2016-01-01 18:29:00.000", end="2016-01-01 18:31:00.000")

        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_item({'entity_id': instance_id,
                                               'end': None,
                                               'entity_type': 'instance',
                                               'flavor': data['flavor'],
                                               'last_event': '2016-01-01 18:30:00+00:00',
                                               'name': data['name'],
                                               'os': {
                                                   'distro': data['os_distro'],
                                                   'os_type': data['os_type'],
                                                   'version': data['os_version']
                                               },
                                               'project_id': project_id,
                                               'start': '2016-01-01 18:30:00+00:00',
                                               'metadata': {}}))

    def test_instance_create_bad_date_format(self):
        instance_create_query = "{url}/project/{project}/instance"
        project_id = "my_test_project_id"
        instance_id = str(uuid4())
        data = {'id': instance_id,
                'created_at': 'A_BAD_DATE_FORMAT',
                'name': 'integration_test_instance_FlavorA',
                'flavor': 'FlavorA',
                'os_type': 'Linux',
                'os_distro': 'Ubuntu',
                'os_version': '14.04'}

        response = self.almanachHelper.post(url=instance_create_query, data=data, project=project_id)

        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                'error',
                'The provided date has an invalid format. Format should be of yyyy-mm-ddThh:mm:ss.msZ, '
                'ex: 2015-01-31T18:24:34.1523Z'
        ))

    def test_instance_create_missing_flavor_param(self):
        instance_create_query = "{url}/project/{project}/instance"
        project_id = "my_test_project_id"
        instance_id = str(uuid4())
        data = {'id': instance_id,
                'created_at': '2016-01-01T18:30:00Z',
                'name': 'integration_test_instance_FlavorA',
                'os_type': 'Linux',
                'os_distro': 'Ubuntu',
                'os_version': '14.04'}

        response = self.almanachHelper.post(url=instance_create_query, data=data, project=project_id)

        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                "error",
                "The 'flavor' param is mandatory for the request you have made."
        ))

    def test_instance_create_missing_type_name_param(self):
        volume_type_query = "{url}/volume_type"
        volume_type_id = str(uuid4())
        data = dict(
                type_id=volume_type_id
        )

        response = self.almanachHelper.post(url=volume_type_query, data=data)

        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                "error",
                "The 'type_name' param is mandatory for the request you have made."
        ))
