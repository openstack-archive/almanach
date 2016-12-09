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


class TestVolumeSuppressionScenario(base.BaseAlmanachScenarioTest):

    def test_delete_volume(self):
        volume = self.create_volume_without_cleanup()
        self.volumes_client.delete_volume(volume['id'])
        self.volumes_client.wait_for_resource_deletion(volume['id'])

        resp, response_body = self.almanach_client.get_tenant_entities(volume['os-vol-tenant-attr:tenant_id'])
        self.assertEqual(resp.status, 200)

        response_body = json.loads(response_body)
        self.assertIsInstance(response_body, list)
        self.assertEqual(1, len(response_body))
        self.assertEqual(volume['id'], response_body[0]['entity_id'])
        self.assertEqual(volume['volume_type'], response_body[0]['volume_type'])
        self.assertIsNotNone(response_body[0]['start'])
        self.assertIsNotNone(response_body[0]['end'])
