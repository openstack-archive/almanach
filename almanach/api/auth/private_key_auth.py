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

from almanach.api.auth import base_auth
from almanach.core import exception


class PrivateKeyAuthentication(base_auth.BaseAuth):
    def __init__(self, private_key):
        self.private_key = private_key

    def validate(self, token):
        if token is None or self.private_key != token:
            raise exception.AuthenticationFailureException("Invalid Token")
        return True
