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

import unittest

from flexmock import flexmock, flexmock_teardown
from hamcrest import instance_of, assert_that

from almanach import config
from almanach.adapters.auth_adapter import AuthenticationAdapter
from almanach.auth.keystone_auth import KeystoneAuthentication
from almanach.auth.mixed_auth import MixedAuthentication
from almanach.auth.private_key_auth import PrivateKeyAuthentication


class AuthenticationAdapterTest(unittest.TestCase):
    def tearDown(self):
        flexmock_teardown()

    def test_assert_that_the_default_backend_is_private_key(self):
        adapter = AuthenticationAdapter().factory()
        assert_that(adapter, instance_of(PrivateKeyAuthentication))

    def test_get_keystone_auth_backend(self):
        flexmock(config).should_receive("auth_strategy").and_return("keystone")
        adapter = AuthenticationAdapter().factory()
        assert_that(adapter, instance_of(KeystoneAuthentication))

    def test_get_mixed_auth_backend(self):
        flexmock(config).should_receive("auth_strategy").and_return("token,keystone")
        adapter = AuthenticationAdapter().factory()
        assert_that(adapter, instance_of(MixedAuthentication))
