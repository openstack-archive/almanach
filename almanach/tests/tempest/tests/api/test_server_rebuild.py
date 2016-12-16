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

from almanach.tests.tempest.tests.api import base
from oslo_serialization import jsonutils as json


class TestServerRebuild(base.BaseAlmanachTest):
    def setUp(self):
        super(base.BaseAlmanachTest, self).setUp()

    @classmethod
    def resource_setup(cls):
        super(TestServerRebuild, cls).resource_setup()

    def test_server_rebuild(self):
        tenant_id = str(uuid4())
        server = self.get_server_creation_payload()
        self.create_server_through_api(tenant_id, server)

        rebuild_data = {
            'distro': 'Ubuntu',
            'version': '14.04',
            'os_type': 'Linux',
            'rebuild_date': '2016-01-01T18:50:00Z'
        }
        data = json.dumps(rebuild_data)

        self.almanach_client.rebuild(server['id'], data)

        resp, response_body = self.almanach_client.get_tenant_entities(tenant_id)

        entities = json.loads(response_body)
        self.assertIsInstance(entities, list)
        self.assertEqual(2, len(entities))

        rebuilded_server, initial_server = sorted(entities, key=lambda k: k['end'] if k['end'] is not None else '')

        self.assertEqual(server['id'], initial_server['entity_id'])
        self.assertEqual(server['os_version'], initial_server['os']['version'])
        self.assertIsNotNone(initial_server['end'])
        self.assertEqual(server['id'], rebuilded_server['entity_id'])
        self.assertEqual(rebuild_data['version'], rebuilded_server['os']['version'])
        self.assertIsNone(rebuilded_server['end'])
