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
from hamcrest import raises, assert_that, calling, equal_to

from almanach.auth.private_key_auth import PrivateKeyAuthentication
from almanach.common.exceptions.authentication_failure_exception import AuthenticationFailureException


class PrivateKeyAuthenticationTest(unittest.TestCase):
    def setUp(self):
        self.auth_backend = PrivateKeyAuthentication("my token")

    def test_with_correct_token(self):
        assert_that(self.auth_backend.validate("my token"), equal_to(True))

    def test_with_invalid_token(self):
        assert_that(calling(self.auth_backend.validate).with_args("bad token"), raises(AuthenticationFailureException))

    def test_with_empty_token(self):
        assert_that(calling(self.auth_backend.validate).with_args(None), raises(AuthenticationFailureException))
