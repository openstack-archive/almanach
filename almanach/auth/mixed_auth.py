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
from almanach.auth.base_auth import BaseAuth
from almanach.common.exceptions.authentication_failure_exception import AuthenticationFailureException


class MixedAuthentication(BaseAuth):
    def __init__(self, authentication_methods):
        self.authentication_methods = authentication_methods

    def validate(self, token):
        for method in self.authentication_methods:
            try:
                valid = method.validate(token)
                if valid:
                    logging.debug('Validated token with auth {0}'.format(method.__class__))
                    return True
            except AuthenticationFailureException:
                logging.debug('Failed to validate with auth {0}'.format(method.__class__))
        raise AuthenticationFailureException('No valid auth method matching token')
