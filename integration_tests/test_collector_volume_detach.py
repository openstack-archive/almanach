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

import uuid

from hamcrest import has_entry, assert_that, equal_to
from retry import retry

from base_api_volume_testcase import BaseApiVolumeTestCase
from builders import messages


class CollectorVolumeDetachTest(BaseApiVolumeTestCase):
    def test_detach_volume(self):
        tenant_id = str(uuid.uuid4())
        instance_id = str(uuid.uuid4())
        volume_id = str(uuid.uuid4())

        self.rabbitMqHelper.push(message=messages.get_volume_create_end_sample(
                volume_id=volume_id, tenant_id=tenant_id, volume_type=messages.DEFAULT_VOLUME_TYPE))

        self.rabbitMqHelper.push(message=messages.get_volume_attach_kilo_end_sample(
                volume_id=volume_id, tenant_id=tenant_id, attached_to=[instance_id]))

        self.rabbitMqHelper.push(message=messages.get_volume_detach_kilo_end_sample(
                volume_id=volume_id, tenant_id=tenant_id, attached_to=[instance_id]))

        self.assert_that_volume_entity_has_instance_detached(tenant_id)

    @retry(exceptions=AssertionError, delay=1, max_delay=300)
    def assert_that_volume_entity_has_instance_detached(self, tenant_id):
        entities = self.almanachHelper.get_entities(tenant_id, "2016-01-01 00:00:00.000")
        assert_that(len(entities), equal_to(1))
        assert_that(entities[0], has_entry("end", None))
        assert_that(entities[0], has_entry("attached_to", []))
