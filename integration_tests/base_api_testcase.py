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

import unittest

from retry import retry
from uuid import uuid4
from hamcrest import equal_to, assert_that, has_entry

from helpers.rabbit_mq_helper import RabbitMqHelper
from helpers.almanach_helper import AlmanachHelper


class BaseApiTestCase(unittest.TestCase):
    rabbitMqHelper = RabbitMqHelper()
    almanachHelper = AlmanachHelper()

    def _create_instance_entity(self):
        project_id = "my_test_project_id"
        instance_id = str(uuid4())
        data = {
            'id': instance_id,
            'created_at': '2016-01-01T18:30:00Z',
            'name': 'integration_test_instance_FlavorA',
            'flavor': 'FlavorA',
            'os_type': 'FreeBSD',
            'os_distro': 'Stable',
            'os_version': '10',
        }
        response = self.almanachHelper.post(url="{url}/project/{project}/instance", data=data, project=project_id)
        assert_that(response.status_code, equal_to(201))
        return instance_id

    @classmethod
    @retry(exceptions=AssertionError, delay=10, max_delay=300)
    def _wait_until_volume_type_is_created(cls, volume_type_id):
        assert_that(cls._get_volume_types(volume_type_id),
                    has_entry("volume_type_id", volume_type_id))

    @classmethod
    def _get_volume_types(cls, type_id):
        query = "{url}/volume_type/{type_id}"
        response = cls.almanachHelper.get(url=query, type_id=type_id)
        return response.json()
