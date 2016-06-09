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
from hamcrest import raises, assert_that, calling, equal_to

from almanach.auth.keystone_auth import KeystoneAuthentication
from almanach.common.exceptions.authentication_failure_exception import AuthenticationFailureException


class KeystoneAuthenticationTest(unittest.TestCase):
    def setUp(self):
        self.token_manager_factory = flexmock()
        self.keystone_token_manager = flexmock()
        self.auth_backend = KeystoneAuthentication(self.token_manager_factory)

    def tearDown(self):
        flexmock_teardown()

    def test_with_correct_token(self):
        token = "my token"
        self.token_manager_factory.should_receive("get_manager").and_return(self.keystone_token_manager)
        self.keystone_token_manager.should_receive("validate").with_args(token)
        assert_that(self.auth_backend.validate(token), equal_to(True))

    def test_with_invalid_token(self):
        token = "bad token"
        self.token_manager_factory.should_receive("get_manager").and_return(self.keystone_token_manager)
        self.keystone_token_manager.should_receive("validate").with_args(token).and_raise(Exception)
        assert_that(calling(self.auth_backend.validate).with_args(token), raises(AuthenticationFailureException))

    def test_with_empty_token(self):
        assert_that(calling(self.auth_backend.validate).with_args(None), raises(AuthenticationFailureException))
