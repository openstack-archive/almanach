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

import logging

from almanach import config
from almanach.auth.keystone_auth import KeystoneAuthentication, KeystoneTokenManagerFactory
from almanach.auth.private_key_auth import PrivateKeyAuthentication


class AuthenticationAdapter(object):

    @staticmethod
    def factory():
        if config.auth_strategy() == "keystone":
            logging.info("Loading Keystone authentication backend")
            return KeystoneAuthentication(KeystoneTokenManagerFactory(
                username=config.keystone_username(),
                password=config.keystone_password(),
                auth_url=config.keystone_url(),
                tenant_name=config.keystone_tenant_name()
            ))
        else:
            logging.info("Loading PrivateKey authentication backend")
            return PrivateKeyAuthentication(config.auth_private_key())
