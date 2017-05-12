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
        resp, response_body = self.get('/v1/info')
        return resp, response_body

    def create_server(self, tenant_id, body):
        resp, response_body = self.post('/v1/project/{}/instance'.format(tenant_id), body=body)
        return resp, response_body

    def delete_server(self, instance_id, body):
        resp, response_body = self.delete('/v1/instance/{}'.format(instance_id), body=body)
        return resp, response_body

    def get_volume_type(self, volume_type_id):
        resp, response_body = self.get('/v1/volume_type/{}'.format(volume_type_id))
        return resp, response_body

    def create_volume_type(self, body):
        resp, response_body = self.post('/v1/volume_type', body)
        return resp, response_body

    def create_volume(self, tenant_id, body):
        url = '/v1/project/{}/volume'.format(tenant_id)
        resp, response_body = self.post(url, body)
        return resp, response_body

    def delete_volume(self, volume_id, body):
        resp, response_body = self.delete('/v1/volume/{}'.format(volume_id), body=body)
        return resp, response_body

    def resize_volume(self, volume_id, body):
        resp, response_body = self.put('/v1/volume/{}/resize'.format(volume_id), body)
        return resp, response_body

    def attach_volume(self, volume_id, body):
        resp, response_body = self.put('/v1/volume/{}/attach'.format(volume_id), body)
        return resp, response_body

    def detach_volume(self, volume_id, body):
        resp, response_body = self.put('/v1/volume/{}/detach'.format(volume_id), body)
        return resp, response_body

    def get_tenant_entities(self, tenant_id):
        url = '/v1/project/{}/entities?start=2016-01-01%2000:00:00.000'.format(tenant_id)
        resp, response_body = self.get(url)
        return resp, response_body

    def update_server(self, instance_id, body):
        url = '/v1/entity/instance/{}'.format(instance_id)
        resp, response_body = self.put(url, body)
        return resp, response_body

    def rebuild(self, instance_id, body):
        update_instance_rebuild_query = "/v1/instance/{}/rebuild".format(instance_id)
        resp, response_body = self.put(update_instance_rebuild_query, body)
        return resp, response_body

    def resize(self, instance_id, body):
        url = "/v1/instance/{}/resize".format(instance_id)
        resp, response_body = self.put(url, body)
        return resp, response_body
