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

import six
import voluptuous

from almanach.core import exception


class InstanceValidator(object):
    def __init__(self):
        self.schema = voluptuous.Schema({
            'name': six.text_type,
            'flavor': six.text_type,
            'os': {
                voluptuous.Required('distro'): six.text_type,
                voluptuous.Required('version'): six.text_type,
                voluptuous.Required('os_type'): six.text_type,
            },
            'metadata': dict,
            'start_date': voluptuous.Datetime(),
            'end_date': voluptuous.Datetime(),
        })

    def validate_update(self, payload):
        try:
            return self.schema(payload)
        except voluptuous.MultipleInvalid as e:
            raise exception.InvalidAttributeException(e.errors)
