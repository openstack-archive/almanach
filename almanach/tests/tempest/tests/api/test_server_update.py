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


class TestServerUpdate(base.BaseAlmanachTest):

    def setUp(self):
        super(base.BaseAlmanachTest, self).setUp()

    @classmethod
    def resource_setup(cls):
        super(TestServerUpdate, cls).resource_setup()

    def test_instance_update(self):
        server = self.get_server_creation_payload()
        self.create_server_through_api(str(uuid4()), server)

        update_field = json.dumps({'start_date': '2016-04-14T18:30:00.00Z',
                                   'flavor': 'NewFlavor'})
        resp, response_body = self.almanach_client.update_server(server['id'], update_field)

        updated_server = json.loads(response_body)

        self.assertEqual(server['id'], updated_server['entity_id'])
        self.assertEqual('2016-04-14 18:30:00+00:00', updated_server['start'])
        self.assertEqual('NewFlavor', updated_server['flavor'])
