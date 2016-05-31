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

from base_api_testcase import BaseApiTestCase
from builders import messages
from helpers.mongo_helper import MongoHelper


class BaseApiVolumeTestCase(BaseApiTestCase):

    @classmethod
    def setUpClass(cls):
        cls.setup_volume_type()

    @classmethod
    def tearDownClass(cls):
        MongoHelper().drop_database()

    @classmethod
    def setup_volume_type(cls):
        cls.rabbitMqHelper.push(
                message=messages.get_volume_type_create_sample(volume_type_id=messages.DEFAULT_VOLUME_TYPE,
                                                               volume_type_name=messages.DEFAULT_VOLUME_TYPE),
        )
        cls._wait_until_volume_type_is_created(volume_type_id=messages.DEFAULT_VOLUME_TYPE)
