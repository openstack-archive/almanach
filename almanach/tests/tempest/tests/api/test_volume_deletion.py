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
from oslo_utils import timeutils

from almanach.tests.tempest.tests.api import base


class TestVolumeDeletion(base.BaseAlmanachTest):

    @classmethod
    def resource_setup(cls):
        super(TestVolumeDeletion, cls).resource_setup()

    def test_delete_volume(self):
        resp, tenant_id, volume = self.create_volume()
        self.assertEqual(resp.status, 201)

        delete_body = {'date': timeutils.isotime()}
        resp, _ = self.almanach_client.delete_volume(volume['volume_id'], json.dumps(delete_body))
        self.assertEqual(resp.status, 202)

        resp, response_body = self.almanach_client.get_tenant_entities(tenant_id)
        response_body = json.loads(response_body)

        self.assertEqual(resp.status, 200)
        self.assertIsInstance(response_body, list)
        self.assertEqual(1, len(response_body))
        self.assertEqual(volume['volume_id'], response_body[0]['entity_id'])
        self.assertEqual('volume', response_body[0]['entity_type'])
        self.assertIsNotNone(response_body[0]['end'])
