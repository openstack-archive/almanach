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
import uuid

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_entry
from hamcrest import is_not
import pytz
from retry import retry

from base_api_testcase import BaseApiTestCase
from builders.messages import get_instance_create_end_sample
from builders.messages import get_instance_delete_end_sample


class CollectorInstanceDeleteTest(BaseApiTestCase):
    def test_instance_delete(self):
        tenant_id = str(uuid.uuid4())
        instance_id = str(uuid.uuid4())

        self.rabbitMqHelper.push(
            get_instance_create_end_sample(
                instance_id=instance_id,
                tenant_id=tenant_id,
                creation_timestamp=datetime(2016, 2, 1, 9, 0, 0, tzinfo=pytz.utc)
            ))

        self.rabbitMqHelper.push(
            get_instance_delete_end_sample(
                instance_id=instance_id,
                tenant_id=tenant_id,
                deletion_timestamp=datetime(2016, 2, 1, 10, 0, 0, tzinfo=pytz.utc)
            ))

        self.assert_instance_entity_is_closed(tenant_id)

    @retry(exceptions=AssertionError, delay=1, max_delay=300)
    def assert_instance_entity_is_closed(self, tenant_id):
        entities = self.almanachHelper.get_entities(tenant_id, "2016-01-01 00:00:00.000")
        assert_that(len(entities), equal_to(1))
        assert_that(entities[0], is_not(has_entry("end", None)))
