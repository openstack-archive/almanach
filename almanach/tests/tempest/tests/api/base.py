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

from tempest import config
import tempest.test

from almanach.tests.tempest import clients

CONF = config.CONF


class BaseAlmanachTest(tempest.test.BaseTestCase):

    credentials = ['primary']

    @classmethod
    def skip_checks(cls):
        super(BaseAlmanachTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        cls.set_network_resources()
        super(BaseAlmanachTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseAlmanachTest, cls).setup_clients()
        cls.servers_client = cls.os_primary.servers_client
        cls.flavors_client = cls.os_primary.flavors_client
        cls.image_client = cls.os_primary.image_client
