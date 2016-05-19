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

import json
import time
import uuid
import pytz

from datetime import datetime
from hamcrest import assert_that, equal_to
from builders import messages
from helpers.rabbit_mq_helper import RabbitMqHelper
from helpers.almanach_helper import AlmanachHelper
from helpers.mongo_helper import MongoHelper
from base_api_testcase import BaseApiTestCase


class CollectorMultiAttachTest(BaseApiTestCase):
    tenant_id = None
    rabbitMqHelper = None

    @classmethod
    def setUpClass(cls):
        cls.almanachHelper = AlmanachHelper()
        cls.rabbitMqHelper = RabbitMqHelper()
        cls.prepare_dataset()

    @classmethod
    def prepare_dataset(cls):
        MongoHelper().drop_database()
        cls.tenant_id = "my-tenant-" + str(uuid.uuid4())
        cls.setup_volume_type()
        cls.setup_attached_kilo_volume(cls.tenant_id)
        cls.setup_detached_kilo_volume(cls.tenant_id)
        time.sleep(5)  # todo replace me with @retry

    @classmethod
    def tearDownClass(cls):
        MongoHelper().drop_database()

    def test_kilo_volume_attach(self):
        entities = self.query_almanach()

        matches = [x for x in entities if x.get('entity_id') == 'attached-volume-kilo']
        assert_that(len(matches), equal_to(1))
        assert_that(len(matches[0].get('attached_to')), equal_to(2))

    def test_kilo_volume_detach(self):
        entities = self.query_almanach()

        detached_matches = [x for x in entities if
                            x.get('entity_id') == 'detached-volume-kilo' and x.get('attached_to') == []]
        assert_that(len(detached_matches), equal_to(2))

        unattached_matches = [x for x in entities if
                              x.get('entity_id') == 'detached-volume-kilo' and x.get('attached_to') == ["my_vm"]]
        assert_that(len(unattached_matches), equal_to(1))

    def query_almanach(self):
        response = self.almanachHelper.get(url="{url}/project/{project}/entities?start={start}",
                                           project=self.tenant_id,
                                           start="2010-01-01 18:50:00.000")

        return json.loads(response.text)

    @classmethod
    def setup_attached_kilo_volume(cls, tenant_id):
        cls.push(message=messages.get_volume_create_end_sample(
            volume_id="attached-volume-kilo", tenant_id=tenant_id, volume_type=messages.DEFAULT_VOLUME_TYPE)
        )

        cls.push(message=messages.get_volume_attach_kilo_end_sample(
            volume_id="attached-volume-kilo", tenant_id=tenant_id, attached_to=["vm1"]))

        cls.push(message=messages.get_volume_attach_kilo_end_sample(
            volume_id="attached-volume-kilo", tenant_id=tenant_id, attached_to=["vm1", "vm2"]))

    @classmethod
    def setup_detached_kilo_volume(cls, tenant_id):
        cls.push(message=messages.get_volume_create_end_sample(
            volume_id="detached-volume-kilo", tenant_id=tenant_id, volume_type=messages.DEFAULT_VOLUME_TYPE)
        )

        cls.push(message=messages.get_volume_attach_kilo_end_sample(
            volume_id="detached-volume-kilo", tenant_id=tenant_id, attached_to=["my_vm"],
            timestamp=datetime(2015, 7, 29, 8, 1, 59, tzinfo=pytz.utc)))

        cls.push(message=messages.get_volume_detach_kilo_end_sample(
            volume_id="detached-volume-kilo", tenant_id=tenant_id, attached_to=[],
            timestamp=datetime(2015, 7, 30, 8, 1, 59, tzinfo=pytz.utc)))

    @classmethod
    def setup_volume_type(cls):
        cls.push(message=messages.get_volume_type_create_sample(
            volume_type_id=messages.DEFAULT_VOLUME_TYPE, volume_type_name=messages.DEFAULT_VOLUME_TYPE))

    @classmethod
    def push(cls, message):
        cls.rabbitMqHelper.push(message)
