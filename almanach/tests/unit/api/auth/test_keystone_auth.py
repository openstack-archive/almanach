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

from keystoneauth1 import exceptions as keystoneauth1_exceptions

from almanach.api.auth import keystone_auth
from almanach.core import exception
from almanach.tests.unit import base


class TestKeystoneAuthentication(base.BaseTestCase):

    def setUp(self):
        super(TestKeystoneAuthentication, self).setUp()
        self.session_mock = mock.patch('keystoneauth1.session.Session').start()
        self.keystone_mock = mock.patch('keystoneclient.v3.client.Client').start()

        self.validation_mock = mock.Mock()
        self.keystone_mock.return_value.tokens.validate = self.validation_mock

        self.driver = keystone_auth.KeystoneAuthentication(self.config)

    def test_with_correct_token(self):
        token = 'some keystone token'
        self.validation_mock.return_value = True
        self.driver.validate(token)
        self.validation_mock.assert_called_once_with(token)

    def test_with_invalid_token(self):
        token = 'some keystone token'
        self.validation_mock.return_value = False
        self.assertRaises(exception.AuthenticationFailureException, self.driver.validate, token)
        self.validation_mock.assert_called_once_with(token)

    def test_with_http_error(self):
        token = 'some keystone token'
        self.validation_mock.side_effect = keystoneauth1_exceptions.HttpError(message='Some Error')
        self.assertRaises(exception.AuthenticationFailureException, self.driver.validate, token)
        self.validation_mock.assert_called_once_with(token)

    def test_with_empty_token(self):
        token = None
        self.assertRaises(exception.AuthenticationFailureException, self.driver.validate, token)
