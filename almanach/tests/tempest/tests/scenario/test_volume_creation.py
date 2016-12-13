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


class TestVolumeCreationScenario(base.BaseAlmanachScenarioTest):

    def test_create_volume(self):
        volume = self.create_volume()

        entities = self.get_tenant_entities(volume['os-vol-tenant-attr:tenant_id'])
        self.assertEqual(1, len(entities))
        self.assertEqual(volume['id'], entities[0]['entity_id'])
        self.assertEqual(volume['volume_type'], entities[0]['volume_type'])
        self.assertIsNotNone(entities[0]['start'])
        self.assertIsNone(entities[0]['end'])
