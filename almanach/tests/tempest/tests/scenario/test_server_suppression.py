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

from oslo_serialization import jsonutils as json

from almanach.tests.tempest.tests.scenario import base


class TestServerSuppressionScenario(base.BaseAlmanachScenarioTest):

    def test_delete_server(self):
        server, flavor = self.create_test_server(wait_until='ACTIVE')
        self.delete_test_server(server)

        resp, response_body = self.almanach_client.get_tenant_entities(server['tenant_id'])
        self.assertEqual(resp.status, 200)

        response_body = json.loads(response_body)
        self.assertIsInstance(response_body, list)
        self.assertEqual(1, len(response_body))

        self.assertEqual(server['id'], response_body[0]['entity_id'])
        self.assertEqual('instance', response_body[0]['entity_type'])
        self.assertEqual(server['name'], response_body[0]['name'])
        self.assertEqual(flavor['name'], response_body[0]['flavor'])
        self.assertIsNotNone(response_body[0]['start'])
        self.assertIsNotNone(response_body[0]['end'])
