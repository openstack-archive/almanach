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

from flexmock import flexmock
from hamcrest import assert_that
from hamcrest import calling
from hamcrest import equal_to
from hamcrest import raises

from almanach.api.auth import keystone_auth
from almanach.core import exception

from tests import base


class KeystoneAuthenticationTest(base.BaseTestCase):

    def setUp(self):
        super(KeystoneAuthenticationTest, self).setUp()
        self.token_manager_factory = flexmock()
        self.keystone_token_manager = flexmock()
        self.auth_backend = keystone_auth.KeystoneAuthentication(self.token_manager_factory)

    def test_with_correct_token(self):
        token = "my token"
        self.token_manager_factory.should_receive("get_manager").and_return(self.keystone_token_manager)
        self.keystone_token_manager.should_receive("validate").with_args(token)
        assert_that(self.auth_backend.validate(token), equal_to(True))

    def test_with_invalid_token(self):
        token = "bad token"
        self.token_manager_factory.should_receive("get_manager").and_return(self.keystone_token_manager)
        self.keystone_token_manager.should_receive("validate").with_args(token).and_raise(Exception)
        assert_that(calling(self.auth_backend.validate)
                    .with_args(token), raises(exception.AuthenticationFailureException))

    def test_with_empty_token(self):
        assert_that(calling(self.auth_backend.validate)
                    .with_args(None), raises(exception.AuthenticationFailureException))
