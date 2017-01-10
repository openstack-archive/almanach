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

from tempest.common import waiters
from tempest.lib.common.utils import test_utils

from almanach.tests.tempest.tests.scenario import base


class TestServerResizeScenario(base.BaseAlmanachScenarioTest):

    def test_resize_server(self):
        server, initial_flavor, resized_flavor = self._resize_server()
        self.wait_for_notification(self._check_that_a_new_entity_is_created,
                                   server)

        entities = self.get_tenant_entities(server['tenant_id'])
        self.assertEqual(2, len(entities))

        self.assertEqual(server['id'], entities[0]['entity_id'])
        self.assertEqual('instance', entities[0]['entity_type'])
        self.assertEqual(server['name'], entities[0]['name'])
        self.assertEqual(initial_flavor['name'], entities[0]['flavor'])
        self.assertIsNotNone(entities[0]['start'])
        self.assertIsNotNone(entities[0]['end'])
        self.assertEqual(dict(), entities[0]['os'])
        self.assertEqual(dict(), entities[0]['image_meta'])

        self.assertEqual(server['id'], entities[1]['entity_id'])
        self.assertEqual('instance', entities[1]['entity_type'])
        self.assertEqual(server['name'], entities[1]['name'])
        self.assertEqual(resized_flavor['name'], entities[1]['flavor'])
        self.assertIsNotNone(entities[1]['start'])
        self.assertIsNone(entities[1]['end'])
        self.assertEqual(dict(), entities[0]['os'])
        self.assertEqual(dict(), entities[0]['image_meta'])

    def _check_that_a_new_entity_is_created(self, server):
        entities = self.get_tenant_entities(server['tenant_id'])
        return len(entities) == 2

    def _resize_server(self):
        flavors = self.flavors_client.list_flavors()['flavors']
        resized_flavor = flavors[1]
        server, initial_flavor = self.create_test_server(wait_until='ACTIVE')
        self.os.servers_client.resize_server(server['id'], resized_flavor['id'])

        waiters.wait_for_server_status(self.os.servers_client, server['id'],
                                       status='VERIFY_RESIZE')

        self.os.servers_client.confirm_resize_server(server['id'])

        waiters.wait_for_server_status(self.os.servers_client, server['id'],
                                       status='ACTIVE')

        self.addCleanup(waiters.wait_for_server_termination,
                        self.os.servers_client, server['id'])
        self.addCleanup(test_utils.call_and_ignore_notfound_exc,
                        self.os.servers_client.delete_server, server['id'])

        return server, initial_flavor, resized_flavor
