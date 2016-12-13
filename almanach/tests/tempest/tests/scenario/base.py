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

from oslo_log import log
from tempest.common.utils import data_utils
from tempest.common import compute
from tempest.common import waiters
from tempest import config
from tempest.scenario import manager

from almanach.tests.tempest import clients

CONF = config.CONF
LOG = log.getLogger(__name__)


class BaseAlmanachScenarioTest(manager.ScenarioTest):

    credentials = ['primary', 'admin']

    @classmethod
    def setup_clients(cls):
        super(BaseAlmanachScenarioTest, cls).setup_clients()
        cred_provider = cls._get_credentials_provider()
        credentials = cred_provider.get_creds_by_roles(['admin']).credentials
        cls.os = clients.Manager(credentials=credentials)
        cls.almanach_client = cls.os.almanach_client

    def create_volume_type(self, name=None):
        client = self.os_adm.volume_types_v2_client

        if not name:
            name = 'generic'

        randomized_name = data_utils.rand_name('scenario-type-' + name)
        LOG.info('Creating a volume type with name: %s', randomized_name)

        body = client.create_volume_type(name=randomized_name)['volume_type']
        self.assertIn('id', body)
        self.addCleanup(client.delete_volume_type, body['id'])

        LOG.info('Created volume type with ID: %s', body['id'])
        return body

    def create_volume_without_cleanup(self, size=None, name=None, snapshot_id=None,
                                      imageRef=None, volume_type=None):
        if size is None:
            size = CONF.volume.volume_size
        if name is None:
            name = data_utils.rand_name(self.__class__.__name__)
        kwargs = {'display_name': name,
                  'snapshot_id': snapshot_id,
                  'imageRef': imageRef,
                  'volume_type': volume_type,
                  'size': size}
        volume = self.volumes_client.create_volume(**kwargs)['volume']

        waiters.wait_for_volume_status(self.volumes_client,
                                       volume['id'], 'available')

        volume = self.volumes_client.show_volume(volume['id'])['volume']
        LOG.info('Created volume %s with name: %s', volume['id'], volume['display_name'])
        return volume

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
        waiters.wait_for_server_termination(self.os.servers_client, server['id'])
