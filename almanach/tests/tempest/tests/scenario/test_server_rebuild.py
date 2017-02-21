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


class TestServerRebuildScenario(base.BaseAlmanachScenarioTest):

    def tearDown(self):
        super(TestServerRebuildScenario, self).tearDown()
        self._remove_image_metadata()

    def test_rebuild_server(self):
        server, flavor = self._rebuild_server()
        self.wait_for_notification(self._check_that_a_new_entity_is_created,
                                   server)

        entities = self.get_tenant_entities(server['tenant_id'])
        self.assertEqual(2, len(entities))

        self.assertEqual(server['id'], entities[0]['entity_id'])
        self.assertEqual('instance', entities[0]['entity_type'])
        self.assertEqual(server['name'], entities[0]['name'])
        self.assertEqual(flavor['name'], entities[0]['flavor'])
        self.assertIsNotNone(entities[0]['start'])
        self.assertIsNotNone(entities[0]['end'])
        self.assertEqual(dict(), entities[0]['os'])
        self.assertEqual(dict(), entities[0]['image_meta'])

        self.assertEqual(server['id'], entities[1]['entity_id'])
        self.assertEqual('instance', entities[1]['entity_type'])
        self.assertEqual(server['name'], entities[1]['name'])
        self.assertEqual(flavor['name'], entities[1]['flavor'])
        self.assertIsNotNone(entities[1]['start'])
        self.assertIsNone(entities[1]['end'])
        self.assertEqual('linux', entities[1]['image_meta']['distro'])
        self.assertEqual('linux', entities[1]['os']['distro'])

    def _check_that_a_new_entity_is_created(self, server):
        entities = self.get_tenant_entities(server['tenant_id'])
        return len(entities) == 2

    def _rebuild_server(self):
        server, flavor = self.create_test_server(wait_until='ACTIVE')
        image = self._prepare_image()

        self.os.servers_client.rebuild_server(server['id'], image['id'])
        waiters.wait_for_server_status(self.os.servers_client, server['id'],
                                       status='ACTIVE')

        self.addCleanup(waiters.wait_for_server_termination,
                        self.os.servers_client, server['id'])
        self.addCleanup(test_utils.call_and_ignore_notfound_exc,
                        self.os.servers_client.delete_server, server['id'])

        return server, flavor

    def _prepare_image(self):
        images = self.image_client.list_images()['images']
        self.os_adm.compute_images_client.set_image_metadata(images[0]['id'], {'distro': 'linux'})
        return images[0]

    def _remove_image_metadata(self):
        images = self.image_client.list_images()['images']
        self.os_adm.compute_images_client.delete_image_metadata_item(images[0]['id'], 'distro')
