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

import oslo_serialization
from tempest import config
import tempest.test

from almanach.tests.tempest import clients

CONF = config.CONF


class BaseAlmanachTest(tempest.test.BaseTestCase):
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
        cred_provider = cls._get_credentials_provider()
        credentials = cred_provider.get_creds_by_roles(['admin']).credentials
        cls.os = clients.Manager(credentials=credentials)
        cls.almanach_client = cls.os.almanach_client

    @classmethod
    def create_server_through_api(cls, tenant_id, server):
        resp, _ = cls.almanach_client.create_server(tenant_id, oslo_serialization.jsonutils.dumps(server))
        return resp

    @staticmethod
    def get_server_creation_payload():
        server = {'id': str(uuid4()),
                  'created_at': '2016-01-01T18:30:00Z',
                  'name': 'api_test_instance_create',
                  'flavor': 'api_flavor',
                  'os_type': 'linux',
                  'os_distro': 'ubuntu',
                  'os_version': '14.04'}
        return server
