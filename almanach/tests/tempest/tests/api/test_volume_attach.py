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
from oslo_utils import uuidutils

from almanach.tests.tempest.tests.api import base


class TestVolumeAttach(base.BaseAlmanachTest):

    @classmethod
    def resource_setup(cls):
        super(TestVolumeAttach, cls).resource_setup()

    def test_attach(self):
        resp, tenant_id, volume = self.create_volume()
        self.assertEqual(resp.status, 201)

        attached_to_id = uuidutils.generate_uuid()
        attach_data = {'date': '2016-01-01T18:40:00Z', 'attachments': [attached_to_id]}
        resp, _ = self.almanach_client.attach_volume(volume['volume_id'], json.dumps(attach_data))
        self.assertEqual(resp.status, 200)

        resp, response_body = self.almanach_client.get_tenant_entities(tenant_id)
        response_body = json.loads(response_body)

        self.assertEqual(resp.status, 200)
        self.assertIsInstance(response_body, list)
        self.assertEqual(2, len(response_body))

        un_attached_volume = [v for v in response_body if v['attached_to'] == []][0]
        attached_volume = [v for v in response_body if v['attached_to'] != []][0]

        self.assertEqual(volume['volume_id'], attached_volume['entity_id'])
        self.assertEqual(volume['volume_id'], un_attached_volume['entity_id'])
        self.assertEqual('volume', attached_volume['entity_type'])
        self.assertEqual('volume', un_attached_volume['entity_type'])
        self.assertIsNone(attached_volume['end'])
        self.assertIsNotNone(un_attached_volume['end'])
