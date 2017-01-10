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

from almanach.tests.tempest.tests.scenario import base


class TestServerSuppressionScenario(base.BaseAlmanachScenarioTest):

    def test_delete_server(self):
        server, flavor = self.create_test_server(wait_until='ACTIVE')
        self.delete_test_server(server)
        self.wait_for_notification(self._check_entity_is_closed, server)

        entities = self.get_tenant_entities(server['tenant_id'])
        self.assertEqual(1, len(entities))
        self.assertEqual(server['id'], entities[0]['entity_id'])
        self.assertEqual('instance', entities[0]['entity_type'])
        self.assertEqual(server['name'], entities[0]['name'])
        self.assertEqual(flavor['name'], entities[0]['flavor'])
        self.assertIsNotNone(entities[0]['start'])
        self.assertIsNotNone(entities[0]['end'])

    def _check_entity_is_closed(self, server):
        entities = self.get_tenant_entities(server['tenant_id'])
        return len(entities) == 1 and entities[0]['end'] is not None
