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

import os
import pkg_resources

from unittest import TestCase
from hamcrest import assert_that, equal_to

from almanach import config


class ConfigTest(TestCase):

    def setUp(self):
        config.read(pkg_resources.resource_filename("almanach", "resources/config/test.cfg"))

    def test_get_config_file_value(self):
        assert_that("amqp://guest:guest@localhost:5672", equal_to(config.rabbitmq_url()))

    def test_get_value_from_environment_variable(self):
        url = "amqp://openstack:openstack@hostname:5672"
        token = "my_secret"

        os.environ['RABBITMQ_URL'] = url
        os.environ['ALMANACH_AUTH_TOKEN'] = token

        assert_that(url, equal_to(config.rabbitmq_url()))
        assert_that(token, equal_to(config.api_auth_token()))
