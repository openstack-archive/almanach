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

import time

from oslo_serialization import jsonutils as json
from tempest.common import compute
from tempest.common.utils import data_utils
from tempest.common import waiters
from tempest import config
from tempest.lib import exceptions
from tempest.scenario import manager

from almanach.tests.tempest import clients

CONF = config.CONF


class BaseAlmanachScenarioTest(manager.ScenarioTest):
    credentials = ['primary', 'admin']
    notification_interval = 1
    notification_timeout = 30

    @classmethod
    def setup_clients(cls):
        super(BaseAlmanachScenarioTest, cls).setup_clients()
        cred_provider = cls._get_credentials_provider()
        credentials = cred_provider.get_creds_by_roles(['admin']).credentials
        cls.os = clients.Manager(credentials=credentials)
        cls.almanach_client = cls.os.almanach_client

    def get_tenant_entities(self, tenant_id):
        resp, response_body = self.almanach_client.get_tenant_entities(tenant_id)
        self.assertEqual(resp.status, 200)

        response_body = json.loads(response_body)
        self.assertIsInstance(response_body, list)
        return response_body

    def create_test_volume_type(self):
        client = self.os_adm.volume_types_v2_client
        randomized_name = data_utils.rand_name('scenario-volume-type')

        volume_type = client.create_volume_type(name=randomized_name)['volume_type']

        self.assertIn('id', volume_type)
        self.addCleanup(client.delete_volume_type, volume_type['id'])

        return volume_type

    def create_test_volume(self, size=None, volume_type=None):
        name = data_utils.rand_name(self.__class__.__name__)

        if size is None:
            size = CONF.volume.volume_size

        kwargs = {
            'display_name': name,
            'volume_type': volume_type,
            'size': size
        }

        volume = self.volumes_client.create_volume(**kwargs)['volume']
        waiters.wait_for_volume_status(self.volumes_client,
                                       volume['id'], 'available')

        return self.volumes_client.show_volume(volume['id'])['volume']

    def create_test_server(self, wait_until=None):
        flavors = self.flavors_client.list_flavors()['flavors']
        images = self.image_client.list_images()['images']
        tenant_network = self.get_tenant_network()
        body, servers = compute.create_test_server(
            self.os,
            wait_until=wait_until,
            image_id=images[0]['id'],
            flavor=flavors[0]['id'],
            tenant_network=tenant_network)

        server = self.os.servers_client.show_server(body['id'])['server']
        return server, flavors[0]

    def delete_test_server(self, server):
        self.os.servers_client.delete_server(server['id'])
        waiters.wait_for_server_termination(self.os.servers_client, server['id'], True)

    def wait_for_notification(self, callback, *args):
        start_time = int(time.time())
        while True:
            if callback(*args):
                return

            if int(time.time()) - start_time >= self.notification_timeout:
                raise exceptions.TimeoutException

            time.sleep(self.notification_interval)
