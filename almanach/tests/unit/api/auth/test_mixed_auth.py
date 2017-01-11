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

import mock

from almanach.api.auth import mixed_auth
from almanach.core import exception
from almanach.tests.unit import base


class TestMixedAuthentication(base.BaseTestCase):

    def setUp(self):
        super(TestMixedAuthentication, self).setUp()
        self.auth_one = mock.Mock()
        self.auth_two = mock.Mock()
        self.auth_backend = mixed_auth.MixedAuthentication([self.auth_one, self.auth_two])

    def tearDown(self):
        super(TestMixedAuthentication, self).tearDown()

    def test_with_token_valid_with_auth_one(self):
        token = "my token"
        self.auth_one.validate.return_value = True

        self.assertEqual(self.auth_backend.validate(token), True)
        self.auth_one.validate.assert_called_once()

    def test_with_token_valid_with_auth_two(self):
        token = "my token"
        self.auth_one.validate.side_effect = exception.AuthenticationFailureException
        self.auth_two.validate.return_value = True

        self.assertEqual(self.auth_backend.validate(token), True)
        self.auth_one.validate.assert_called_once()
        self.auth_two.validate.assert_called_once()

    def test_with_token_valid_with_auth_twos(self):
        token = "bad token"
        self.auth_one.validate.side_effect = exception.AuthenticationFailureException
        self.auth_two.validate.side_effect = exception.AuthenticationFailureException

        self.assertRaises(exception.AuthenticationFailureException, self.auth_backend.validate, token)
        self.auth_one.validate.assert_called_once()
        self.auth_two.validate.assert_called_once()
