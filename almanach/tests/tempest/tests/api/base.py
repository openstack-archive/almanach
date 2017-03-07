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

from oslo_serialization import jsonutils as json
from tempest import config
from tempest.lib.common.utils import data_utils
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
        resp, _ = cls.almanach_client.create_server(tenant_id, json.dumps(server))
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

    @staticmethod
    def get_volume_creation_payload(volume_type_name):
        return {'volume_id': str(uuid4()),
                'attached_to': [],
                'volume_name': 'a-test-volume',
                'volume_type': volume_type_name,
                'start': '2016-01-01T18:00:00Z',
                'size': 100}

    def create_volume_type(self):
        volume_type = {'type_id': str(uuid4()),
                       'type_name': data_utils.rand_name('scenario-volume-type')}
        volume_type_body = json.dumps(volume_type)
        return volume_type, self.almanach_client.create_volume_type(volume_type_body)

    def create_volume(self):
        volume_type, _ = self.create_volume_type()
        tenant_id = str(uuid4())
        volume = self.get_volume_creation_payload(volume_type['type_id'])
        resp, response_body = self.almanach_client.create_volume(tenant_id, json.dumps(volume))
        return resp, tenant_id, volume
