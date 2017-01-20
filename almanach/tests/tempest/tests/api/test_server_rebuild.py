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

from almanach.tests.tempest.tests.api import base


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

        data = {
            'distro': 'debian',
            'version': '8.0',
            'os_type': 'linux',
            'rebuild_date': '2016-01-01T18:50:00Z'
        }

        self.almanach_client.rebuild(server['id'],
                                     json.dumps(data))

        resp, response_body = self.almanach_client.get_tenant_entities(tenant_id)

        entities = json.loads(response_body)
        self.assertIsInstance(entities, list)
        self.assertEqual(2, len(entities))

        rebuilt_server, initial_server = sorted(entities, key=lambda k: k['end'] if k['end'] is not None else '')

        self.assertEqual(server['id'], initial_server['entity_id'])
        self.assertIsNotNone(initial_server['end'])

        self.assertEqual(server['os_distro'], initial_server['os']['distro'])
        self.assertEqual(server['os_version'], initial_server['os']['version'])
        self.assertEqual(server['os_type'], initial_server['os']['os_type'])

        self.assertEqual(server['os_distro'], initial_server['image_meta']['distro'])
        self.assertEqual(server['os_version'], initial_server['image_meta']['version'])
        self.assertEqual(server['os_type'], initial_server['image_meta']['os_type'])

        self.assertEqual(server['id'], rebuilt_server['entity_id'])
        self.assertIsNone(rebuilt_server['end'])

        self.assertEqual(data['distro'], rebuilt_server['os']['distro'])
        self.assertEqual(data['version'], rebuilt_server['os']['version'])
        self.assertEqual(data['os_type'], rebuilt_server['os']['os_type'])

        self.assertEqual(data['distro'], rebuilt_server['image_meta']['distro'])
        self.assertEqual(data['version'], rebuilt_server['image_meta']['version'])
        self.assertEqual(data['os_type'], rebuilt_server['image_meta']['os_type'])
