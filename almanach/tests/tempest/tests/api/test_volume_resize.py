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

from almanach.tests.tempest.tests.api import base


class TestVolumeResize(base.BaseAlmanachTest):

    @classmethod
    def resource_setup(cls):
        super(TestVolumeResize, cls).resource_setup()

    def test_resize(self):
        resp, tenant_id, volume = self.create_volume()
        self.assertEqual(resp.status, 201)

        resize_data = {'date': '2016-01-01T18:40:00Z',
                       'size': 150}
        resp, _ = self.almanach_client.resize_volume(volume['volume_id'], json.dumps(resize_data))
        self.assertEqual(resp.status, 200)

        resp, response_body = self.almanach_client.get_tenant_entities(tenant_id)
        response_body = json.loads(response_body)

        self.assertEqual(resp.status, 200)
        self.assertIsInstance(response_body, list)
        self.assertEqual(2, len(response_body))
        initial_volume = [v for v in response_body if v['size'] == 100][0]
        resized_volume = [v for v in response_body if v['size'] == 150][0]
        self.assertEqual(volume['volume_id'], initial_volume['entity_id'])
        self.assertEqual(volume['volume_id'], resized_volume['entity_id'])
        self.assertEqual('volume', initial_volume['entity_type'])
        self.assertEqual('volume', resized_volume['entity_type'])
        self.assertIsNotNone(initial_volume['end'])
        self.assertIsNone(resized_volume['end'])
