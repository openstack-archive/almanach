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

from almanach.api.auth import mixed_auth
from almanach.core import exception

from tests import base


class MixedAuthenticationTest(base.BaseTestCase):

    def setUp(self):
        super(MixedAuthenticationTest, self).setUp()
        self.auth_one = flexmock()
        self.auth_two = flexmock()
        self.auth_backend = mixed_auth.MixedAuthentication([self.auth_one, self.auth_two])

    def test_with_token_valid_with_auth_one(self):
        token = "my token"
        self.auth_one.should_receive("validate").and_return(True)
        assert_that(self.auth_backend.validate(token), equal_to(True))

    def test_with_token_valid_with_auth_two(self):
        token = "my token"
        self.auth_one.should_receive("validate").and_raise(exception.AuthenticationFailureException)
        self.auth_two.should_receive("validate").and_return(True)
        assert_that(self.auth_backend.validate(token), equal_to(True))

    def test_with_token_valid_with_auth_twos(self):
        token = "bad token"
        self.auth_one.should_receive("validate").and_raise(exception.AuthenticationFailureException)
        self.auth_two.should_receive("validate").and_raise(exception.AuthenticationFailureException)
        assert_that(calling(self.auth_backend.validate)
                    .with_args(token), raises(exception.AuthenticationFailureException))
