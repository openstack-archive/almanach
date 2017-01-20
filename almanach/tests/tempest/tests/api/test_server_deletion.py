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


class TestServerDeletion(base.BaseAlmanachTest):

    def setUp(self):
        super(base.BaseAlmanachTest, self).setUp()

    @classmethod
    def resource_setup(cls):
        super(TestServerDeletion, cls).resource_setup()

    def test_instance_delete(self):
        tenant_id = str(uuid4())
        server = self.get_server_creation_payload()
        self.create_server_through_api(tenant_id, server)

        self.almanach_client.delete_server(server['id'],
                                           json.dumps({'date': '2016-01-01T19:50:00Z'}))
        _, response_body = self.almanach_client.get_tenant_entities(tenant_id)

        response_body = json.loads(response_body)
        self.assertIsInstance(response_body, list)
        self.assertEqual(1, len(response_body))

        self.assertEqual(server['id'], response_body[0]['entity_id'])
        self.assertIsNotNone(response_body[0]['end'])
