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

from datetime import datetime
from uuid import uuid4

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_entry
import pytz

from integration_tests.base_api_testcase import BaseApiTestCase
from integration_tests.builders.messages import get_instance_create_end_sample


class MetadataInstanceCreateTest(BaseApiTestCase):
    def test_instance_create_with_metadata(self):
        instance_id = str(uuid4())
        tenant_id = str(uuid4())

        self.rabbitMqHelper.push(
            get_instance_create_end_sample(
                instance_id=instance_id,
                tenant_id=tenant_id,
                creation_timestamp=datetime(2016, 2, 1, 9, 0, 0, tzinfo=pytz.utc),
                metadata={"metering.billing_mode": "42"}
            ))

        self.assert_that_instance_entity_is_created_and_have_proper_metadata(instance_id, tenant_id)

    def assert_that_instance_entity_is_created_and_have_proper_metadata(self, instance_id, tenant_id):
        entities = self.almanachHelper.get_entities(tenant_id, "2016-01-01 00:00:00.000")
        assert_that(len(entities), equal_to(1))
        assert_that(entities[0], has_entry("entity_id", instance_id))
        assert_that(entities[0], has_entry("metadata", {'metering.billing_mode': '42'}))
