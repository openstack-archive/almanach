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


class TestVolumeDetach(base.BaseAlmanachTest):

    @classmethod
    def resource_setup(cls):
        super(TestVolumeDetach, cls).resource_setup()

    def test_detach(self):
        resp, tenant_id, volume = self.create_volume()
        self.assertEqual(resp.status, 201)

        attached_to_id = str(uuid4())
        date = '2016-01-01 18:30:00+00:00'
        attach_data = {'date': '2016-01-01T18:30:00Z', 'attachments': [attached_to_id]}
        resp, _ = self.almanach_client.attach_volume(volume['volume_id'], json.dumps(attach_data))
        self.assertEqual(resp.status, 200)
        detach_data = {'date': '2016-01-01T18:40:00Z',
                       'attachments': []}

        resp, _ = self.almanach_client.detach_volume(volume['volume_id'], json.dumps(detach_data))
        self.assertEqual(resp.status, 200)

        resp, response_body = self.almanach_client.get_tenant_entities(tenant_id)
        response_body = json.loads(response_body)

        self.assertEqual(resp.status, 200)
        self.assertIsInstance(response_body, list)
        self.assertEqual(3, len(response_body))

        un_attached_volumes = [v for v in response_body if v['attached_to'] == []]
        attached_volume = [v for v in response_body if v['attached_to'] != []][0]

        self.assertEqual(volume['volume_id'], attached_volume['entity_id'])
        self.assertEqual(volume['volume_id'], un_attached_volumes[0]['entity_id'])
        self.assertEqual(volume['volume_id'], un_attached_volumes[1]['entity_id'])
        self.assertEqual('volume', attached_volume['entity_type'])
        self.assertEqual('volume', un_attached_volumes[0]['entity_type'])
        self.assertEqual('volume', un_attached_volumes[1]['entity_type'])
        self.assertIsNotNone(attached_volume['end'])
        self.assertIn(None, [un_attached_volumes[0]['end'], un_attached_volumes[1]['end']])
        self.assertIn(date, [un_attached_volumes[0]['end'], un_attached_volumes[1]['end']])
