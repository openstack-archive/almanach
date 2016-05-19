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
from hamcrest import assert_that, has_entry, equal_to

from base_api_testcase import BaseApiTestCase


class ApiInstanceEntityTest(BaseApiTestCase):
    def test_update_entity_instance_with_multiple_attributes(self):
        instance_id = self._create_instance_entity()

        response = self.almanachHelper.put(url="{url}/entity/instance/{instance_id}",
                                           data={"start_date": "2016-04-14T18:30:00.00Z", "flavor": "FlavorB"},
                                           instance_id=instance_id,
                                           )

        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_entry("entity_id", instance_id))
        assert_that(response.json(), has_entry("start", "2016-04-14 18:30:00+00:00"))
        assert_that(response.json(), has_entry("flavor", "FlavorB"))

    def test_update_entity_instance_with_multiple_wrong_attributes(self):
        instance_id = self._create_instance_entity()

        response = self.almanachHelper.put(url="{url}/entity/instance/{instance_id}",
                                           data={"start_date": "2016-04-14T18:30:00.00Z", "flavor": 123, "os": 123},
                                           instance_id=instance_id,
                                           )

        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), equal_to({"error": {"flavor": "expected unicode", "os": "expected a dictionary"}}))

    def test_update_entity_instance_with_one_attribute(self):
        instance_id = self._create_instance_entity()

        response = self.almanachHelper.put(url="{url}/entity/instance/{instance_id}",
                                           data={"start_date": "2016-04-14T18:30:00.00Z"},
                                           instance_id=instance_id,
                                           )

        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_entry("entity_id", instance_id))
        assert_that(response.json(), has_entry("start", "2016-04-14 18:30:00+00:00"))

    def test_update_entity_instance_with_invalid_attribute(self):
        project_id = "my_test_project_id"
        instance_id = self._create_instance_entity()
        data = {
            'id': instance_id,
            'created_at': '2016-01-01T18:30:00Z',
            'name': 'integration_test_instance_FlavorA',
            'flavor': 'FlavorA',
            'os_type': 'FreeBSD',
            'os_distro': 'Stable',
            'os_version': '10',
        }

        response = self.almanachHelper.post(url="{url}/project/{project}/instance", data=data,
                                            project=project_id)
        assert_that(response.status_code, equal_to(201))

        response = self.almanachHelper.put(url="{url}/entity/instance/{instance_id}",
                                           data={'flavor_flavor': 'FlavorA'},
                                           instance_id=instance_id,
                                           )

        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), equal_to({"error": {"flavor_flavor": "extra keys not allowed"}}))

    def test_update_entity_instance_with_wrong_date_format(self):
        instance_id = self._create_instance_entity()

        response = self.almanachHelper.put(url="{url}/entity/instance/{instance_id}",
                                           data={"start_date": "my date"},
                                           instance_id=instance_id,
                                           )

        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), equal_to(
                {"error": {"start_date": "value does not match expected format %Y-%m-%dT%H:%M:%S.%fZ"}}
        ))

    def test_update_entity_change_flavor_of_closed(self):
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

        self.almanachHelper.post(url=instance_create_query, data=data, project=project_id)
        instance_delete_query = "{url}/instance/{instance_id}"
        delete_data = {'date': '2016-01-01T18:50:00Z'}
        self.almanachHelper.delete(url=instance_delete_query, data=delete_data, instance_id=instance_id)

        response = self.almanachHelper.put(url="{url}/entity/instance/{instance_id}?start={start}&end={end}",
                                           start="2016-01-01 18:29:59.0",
                                           end="2016-01-01 18:50:00.0",
                                           data={"flavor": "FlavorB",
                                                 "end_date": "2016-01-02 18:50:00.0Z"},
                                           instance_id=instance_id,
                                           )
        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_entry("flavor", "FlavorB"))
        assert_that(response.json(), has_entry("end", "2016-01-02 18:50:00+00:00"))
