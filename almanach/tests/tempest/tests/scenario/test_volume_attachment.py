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


class TestVolumeAttachmentScenario(base.BaseAlmanachScenarioTest):
    _server = None
    _volume = None

    def tearDown(self):
        super(TestVolumeAttachmentScenario, self).tearDown()
        self.addCleanup(waiters.wait_for_server_termination,
                        self.os.servers_client, self._server['id'])
        self.addCleanup(test_utils.call_and_ignore_notfound_exc,
                        self.os.servers_client.delete_server, self._server['id'])
        self.addCleanup(self.volumes_client.wait_for_resource_deletion,
                        self._volume['id'])
        self.addCleanup(test_utils.call_and_ignore_notfound_exc,
                        self.volumes_client.delete_volume, self._volume['id'])

    def test_attachment(self):
        self._attach_volume_to_server()
        self.wait_for_notification(self._check_that_volume_is_attached)

        entities = self.get_tenant_entities(self._volume['os-vol-tenant-attr:tenant_id'])
        self.assertIsNotNone(entities[0]['start'])
        self.assertIsNone(entities[0]['end'])
        self.assertTrue(self._server['id'] in entities[0]['attached_to'])

        self._detach_volume_from_server()

        self.wait_for_notification(self._check_that_volume_is_detached)

        entities = self.get_tenant_entities(self._volume['os-vol-tenant-attr:tenant_id'])
        self.assertIsNotNone(entities[0]['start'])
        self.assertIsNone(entities[0]['end'])
        self.assertFalse(self._server['id'] in entities[0]['attached_to'])

    def _check_that_volume_is_attached(self):
        entities = self.get_tenant_entities(self._volume['os-vol-tenant-attr:tenant_id'])
        return len(entities) == 1 and self._server['id'] in entities[0]['attached_to']

    def _check_that_volume_is_detached(self):
        entities = self.get_tenant_entities(self._volume['os-vol-tenant-attr:tenant_id'])
        return len(entities) == 1 and self._server['id'] not in entities[0]['attached_to']

    def _attach_volume_to_server(self):
        self._volume = self.create_test_volume()
        self._server, _ = self.create_test_server(wait_until='ACTIVE')

        self.volumes_client.attach_volume(self._volume['id'],
                                          instance_uuid=self._server['id'],
                                          mountpoint='/dev/vdc')

        waiters.wait_for_volume_status(self.volumes_client,
                                       self._volume['id'], 'in-use')

    def _detach_volume_from_server(self):
        self.volumes_client.detach_volume(self._volume['id'])
        waiters.wait_for_volume_status(self.volumes_client,
                                       self._volume['id'], 'available')
