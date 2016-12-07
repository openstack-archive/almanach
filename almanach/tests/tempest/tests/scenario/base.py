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
        LOG.info("Creating a volume type with name: %s", randomized_name)

        body = client.create_volume_type(name=randomized_name)['volume_type']
        self.assertIn('id', body)
        self.addCleanup(client.delete_volume_type, body['id'])

        LOG.info("Created volume type with ID: %s", body['id'])
        return body
