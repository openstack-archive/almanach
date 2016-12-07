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

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_client

from almanach.api.auth import base_auth
from almanach.core import exception


class KeystoneAuthentication(base_auth.BaseAuth):

    def __init__(self, config):
        auth = v3.Password(username=config.auth.keystone_username,
                           password=config.auth.keystone_password,
                           auth_url=config.auth.keystone_url)
        sess = session.Session(auth=auth)
        self._client = keystone_client.Client(session=sess)

    def validate(self, token):
        if token is None:
            raise exception.AuthenticationFailureException('No token provided')

        result = self._client.tokens.validate(token)

        if not result:
            raise exception.AuthenticationFailureException('Invalid token')

        return True
