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


class TestVolumeResizeScenario(base.BaseAlmanachScenarioTest):

    def test_resize_volume(self):
        volume = self._resize_volume()

        entities = self.get_tenant_entities(volume['os-vol-tenant-attr:tenant_id'])
        self.assertEqual(2, len(entities))

        self.assertEqual(volume['id'], entities[0]['entity_id'])
        self.assertEqual(volume['volume_type'], entities[0]['volume_type'])
        self.assertEqual(1, entities[0]['size'])
        self.assertIsNotNone(entities[0]['start'])
        self.assertIsNotNone(entities[0]['end'])

        self.assertEqual(volume['id'], entities[1]['entity_id'])
        self.assertEqual(volume['volume_type'], entities[1]['volume_type'])
        self.assertEqual(2, entities[1]['size'])
        self.assertIsNotNone(entities[1]['start'])
        self.assertIsNone(entities[1]['end'])

    def _resize_volume(self):
        volume = self.create_test_volume(size=1)
        self.volumes_client.extend_volume(volume['id'], new_size=2)

        waiters.wait_for_volume_status(self.volumes_client,
                                       volume['id'], 'available')

        self.addCleanup(self.volumes_client.wait_for_resource_deletion,
                        volume['id'])
        self.addCleanup(test_utils.call_and_ignore_notfound_exc,
                        self.volumes_client.delete_volume, volume['id'])
        return volume
