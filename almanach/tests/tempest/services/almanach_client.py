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

from tempest import config
from tempest.lib.common import rest_client

CONF = config.CONF


class AlmanachClient(rest_client.RestClient):

    def __init__(self, auth_provider):
        super(AlmanachClient, self).__init__(
                auth_provider,
                CONF.almanach.catalog_type,
                CONF.almanach.region or CONF.identity.region,
                endpoint_type=CONF.almanach.endpoint_type)

    def get_version(self):
        resp, response_body = self.get('info')
        return resp, response_body

    def get_volume_type(self, volume_type_id):
        resp, response_body = self.get('volume_type/{}'.format(volume_type_id))
        return resp, response_body

    def get_tenant_entities(self, tenant_id):
        url = 'project/{}/entities?start=2016-01-01%2000:00:00.000'.format(tenant_id)
        resp, response_body = self.get(url)
        return resp, response_body
