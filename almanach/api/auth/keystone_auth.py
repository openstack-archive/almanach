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

from keystoneclient.v2_0 import client as keystone_client
from keystoneclient.v2_0 import tokens

from almanach.api.auth import base_auth
from almanach.core import exception


class KeystoneTokenManagerFactory(object):
    def __init__(self, config):
        self.auth_url = config.auth.keystone_url
        self.tenant_name = config.auth.keystone_tenant
        self.username = config.auth.keystone_username
        self.password = config.auth.keystone_password

    def get_manager(self):
        return tokens.TokenManager(keystone_client.Client(
            username=self.username,
            password=self.password,
            auth_url=self.auth_url,
            tenant_name=self.tenant_name)
        )


class KeystoneAuthentication(base_auth.BaseAuth):
    def __init__(self, token_manager_factory):
        self.token_manager_factory = token_manager_factory

    def validate(self, token):
        if token is None:
            raise exception.AuthenticationFailureException("No token provided")

        try:
            self.token_manager_factory.get_manager().validate(token)
        except Exception as e:
            raise exception.AuthenticationFailureException(e)

        return True
