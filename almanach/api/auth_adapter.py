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

from almanach.api.auth import keystone_auth
from almanach.api.auth import mixed_auth
from almanach.api.auth import private_key_auth

LOG = log.getLogger(__name__)


class AuthenticationAdapter(object):
    def __init__(self, config):
        self.config = config

    def get_authentication_adapter(self):
        if self.config.auth.strategy == 'keystone':
            return self._get_keystone_auth()
        elif all(auth_method in self.config.auth.strategy for auth_method in ['token', 'keystone']):
            adapters = [self._get_private_key_auth(), self._get_keystone_auth()]
            return mixed_auth.MixedAuthentication(adapters)
        return self._get_private_key_auth()

    def _get_private_key_auth(self):
        LOG.info('Loading PrivateKey authentication adapter')
        return private_key_auth.PrivateKeyAuthentication(self.config.auth.private_key)

    def _get_keystone_auth(self):
        LOG.info('Loading Keystone authentication backend')
        return keystone_auth.KeystoneAuthentication(self.config)
