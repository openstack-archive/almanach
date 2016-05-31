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
from datetime import datetime
from retry.api import retry_call

import pytz
from hamcrest import assert_that, equal_to, has_entry

from base_api_testcase import BaseApiTestCase
from builders.messages import get_instance_create_end_sample


class CollectorInstanceCreateTest(BaseApiTestCase):
    def test_instance_creation(self):
        instance_id = str(uuid4())
        tenant_id = str(uuid4())

        self.rabbitMqHelper.push(
            get_instance_create_end_sample(
                    instance_id=instance_id,
                    tenant_id=tenant_id,
                    creation_timestamp=datetime(2016, 2, 1, 9, 0, 0, tzinfo=pytz.utc)
            ))

        retry_call(self._wait_until_instance_is_created, fargs=[instance_id, tenant_id], delay=10, max_delay=300,
                   exceptions=AssertionError)

    def _wait_until_instance_is_created(self, instance_id, tenant_id):
        list_query = "{url}/project/{project}/instances?start={start}"
        response = self.almanachHelper.get(url=list_query, project=tenant_id, start="2016-01-01 18:29:00.000")
        entities = [entity for entity in response.json() if entity['entity_id'] == instance_id]

        assert_that(response.status_code, equal_to(200))
        assert_that(len(entities), equal_to(1))
        assert_that(entities[0], has_entry("entity_id", instance_id))
