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

from hamcrest import assert_that
from hamcrest import instance_of

from almanach.api.auth import keystone_auth
from almanach.api.auth import mixed_auth
from almanach.api.auth import private_key_auth
from almanach.api import auth_adapter

from tests import base


class AuthenticationAdapterTest(base.BaseTestCase):
    def setUp(self):
        super(AuthenticationAdapterTest, self).setUp()
        self.auth_adapter = auth_adapter.AuthenticationAdapter(self.config)

    def test_assert_that_the_default_backend_is_private_key(self):
        adapter = self.auth_adapter.get_authentication_adapter()
        assert_that(adapter, instance_of(private_key_auth.PrivateKeyAuthentication))

    def test_get_keystone_auth_backend(self):
        self.config_fixture.config(strategy='keystone', group='auth')
        adapter = self.auth_adapter.get_authentication_adapter()
        assert_that(adapter, instance_of(keystone_auth.KeystoneAuthentication))

    def test_get_mixed_auth_backend(self):
        self.config_fixture.config(strategy='token,keystone', group='auth')
        adapter = self.auth_adapter.get_authentication_adapter()
        assert_that(adapter, instance_of(mixed_auth.MixedAuthentication))
