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


class TestServerResize(base.BaseAlmanachTest):

    def setUp(self):
        super(base.BaseAlmanachTest, self).setUp()

    @classmethod
    def resource_setup(cls):
        super(TestServerResize, cls).resource_setup()

    def test_instance_resize(self):
        tenant_id = str(uuid4())
        server = self.get_server_creation_payload()
        self.create_server_through_api(tenant_id, server)

        resize_data = {'date': '2016-01-01T18:40:00Z',
                       'flavor': 'resized_flavor'}
        serialized_data = json.dumps(resize_data)

        self.almanach_client.resize(server['id'], serialized_data)

        resp, response_body = self.almanach_client.get_tenant_entities(tenant_id)

        entities = json.loads(response_body)
        self.assertIsInstance(entities, list)
        self.assertEqual(2, len(entities))

        initial_server, resized_server = sorted(entities,
                                                key=lambda k: k['flavor'] if k['flavor'] == 'resized_flavor' else '')

        self.assertEqual(server['id'], initial_server['entity_id'])
        self.assertEqual(server['flavor'], initial_server['flavor'])
        self.assertEqual(server['id'], resized_server['entity_id'])
        self.assertEqual(resize_data['flavor'], resized_server['flavor'])
