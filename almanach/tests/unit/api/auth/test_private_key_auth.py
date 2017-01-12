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

from almanach.api.auth import private_key_auth
from almanach.core import exception
from almanach.tests.unit import base


class TestPrivateKeyAuthentication(base.BaseTestCase):

    def setUp(self):
        super(TestPrivateKeyAuthentication, self).setUp()
        self.auth_backend = private_key_auth.PrivateKeyAuthentication("my token")

    def test_with_correct_token(self):
        self.assertEqual(self.auth_backend.validate("my token"), True)

    def test_with_invalid_token(self):
        self.assertRaises(exception.AuthenticationFailureException, self.auth_backend.validate, "bad token")

    def test_with_empty_token(self):
        self.assertRaises(exception.AuthenticationFailureException, self.auth_backend.validate, None)
