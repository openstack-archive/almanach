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

from base_api_testcase import BaseApiTestCase


class ApiInstanceEntityTest(BaseApiTestCase):
    def test_head_entity_by_id_with_entity_return_200(self):
        instance_id = self._create_instance_entity()
        response = self.almanachHelper.head(url="{url}/entity/{instance_id}",
                                            instance_id=instance_id)

        assert_that(response.status_code, equal_to(200))

    def test_head_entity_by_id_without_entity_return_404(self):
        instance_id = "some_uuid"
        response = self.almanachHelper.head(url="{url}/entity/{instance_id}",
                                            instance_id=instance_id)

        assert_that(response.status_code, equal_to(404))

    def test_get_entity_by_id_with_entity_return_200(self):
        instance_id = self._create_instance_entity()
        response = self.almanachHelper.get(url="{url}/entity/{instance_id}", instance_id=instance_id)

        result = response.json()
        assert_that(response.status_code, equal_to(200))
        assert_that(len(result), equal_to(1))
        assert_that(result[0]["entity_id"], equal_to(instance_id))

    def test_get_entity_by_id_with_entity_return_404(self):
        response = self.almanachHelper.get(url="{url}/entity/{instance_id}", instance_id="foobar")

        result = response.json()
        assert_that(result, equal_to({"error": "Entity not found"}))
        assert_that(response.status_code, equal_to(404))
