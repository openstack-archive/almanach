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

from oslo_log import log
from oslo_serialization import jsonutils as json
from tempest import config

from almanach.tests.tempest.tests.scenario import base

CONF = config.CONF
LOG = log.getLogger(__name__)


class TestVolumeTypeScenario(base.BaseAlmanachScenarioTest):

    def test_create_volume_type(self):
        volume_type = self.create_volume_type(name='my_custom_volume_type')
        LOG.info(volume_type)

        resp, response_body = self.almanach_client.get_volume_type(volume_type['id'])
        self.assertEqual(resp.status, 200)

        response_body = json.loads(response_body)
        self.assertIsInstance(response_body, dict)
        self.assertEqual(volume_type['id'], response_body['volume_type_id'])
        self.assertEqual(volume_type['name'], response_body['volume_type_name'])
