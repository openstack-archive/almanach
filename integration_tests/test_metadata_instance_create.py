from uuid import uuid4
from datetime import datetime
from hamcrest import assert_that, has_entry
from hamcrest import equal_to
from integration_tests.base_api_testcase import BaseApiTestCase
from integration_tests.builders.messages import get_instance_create_end_sample
import pytz


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
