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
from tempest.lib import exceptions

from almanach.tests.tempest.tests.api import base


class TestServerCreation(base.BaseAlmanachTest):
    tenant_id = ''

    def setUp(self):
        super(base.BaseAlmanachTest, self).setUp()
        self.tenant_id = str(uuid4())

    @classmethod
    def resource_setup(cls):
        super(TestServerCreation, cls).resource_setup()

    def test_instance_create(self):
        server = self.get_server_creation_payload()

        resp = self.create_server_through_api(self.tenant_id, server)
        self.assertEqual(resp.status, 201)

        _, response_body = self.almanach_client.get_tenant_entities(self.tenant_id)

        response_body = json.loads(response_body)
        self.assertIsInstance(response_body, list)
        self.assertEqual(1, len(response_body))

        self.assertEqual(server['id'], response_body[0]['entity_id'])
        self.assertIsNone(response_body[0]['end'])

    def test_instance_create_bad_date_format(self):
        server = self.get_server_creation_payload()
        server['created_at'] = 'not_a_real_date'
        exception = None
        try:
            self.create_server_through_api(self.tenant_id, server)
        except exceptions.BadRequest as bad_request:
            exception = bad_request

        self.assertIsNotNone(exception)
        self.assertEqual('400', exception.resp['status'])
        self.assertIn('The provided date has an invalid format. Format should be of yyyy-mm-ddThh:mm:ss.msZ',
                      exception.resp_body['error'])
