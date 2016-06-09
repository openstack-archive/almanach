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

from hamcrest import assert_that, equal_to, has_entries, has_key, is_
from voluptuous import Invalid

from almanach.common.exceptions.validation_exception import InvalidAttributeException
from tests.builder import instance, a
from tests.api.base_api import BaseApi


class ApiEntityTest(BaseApi):

    def test_update_instance_entity_with_a_new_start_date(self):
        data = {
            "start_date": "2014-01-01 00:00:00.0000",
        }

        self.controller.should_receive('update_active_instance_entity') \
            .with_args(
                instance_id="INSTANCE_ID",
                start_date=data["start_date"],
        ).and_return(a(instance().with_id('INSTANCE_ID').with_start(2014, 01, 01, 00, 0, 00)))

        code, result = self.api_put(
                '/entity/instance/INSTANCE_ID',
                headers={'X-Auth-Token': 'some token value'},
                data=data,
        )

        assert_that(code, equal_to(200))
        assert_that(result, has_key('entity_id'))
        assert_that(result, has_key('start'))
        assert_that(result, has_key('end'))
        assert_that(result['start'], is_("2014-01-01 00:00:00+00:00"))

    def test_update_active_instance_entity_with_wrong_attribute_raise_exception(self):
        errors = [
            Invalid(message="error message1", path=["my_attribute1"]),
            Invalid(message="error message2", path=["my_attribute2"]),
        ]

        formatted_errors = {
            "my_attribute1": "error message1",
            "my_attribute2": "error message2",
        }

        instance_id = 'INSTANCE_ID'
        data = {
            'flavor': 'A_FLAVOR',
        }

        self.controller.should_receive('update_active_instance_entity') \
            .with_args(instance_id=instance_id, **data) \
            .once() \
            .and_raise(InvalidAttributeException(errors))

        code, result = self.api_put(
                '/entity/instance/INSTANCE_ID',
                data=data,
                headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries({
            "error": formatted_errors
        }))
        assert_that(code, equal_to(400))

    def test_entity_head_with_existing_entity(self):
        entity_id = "entity_id"
        self.controller.should_receive('entity_exists') \
            .and_return(True)

        code, result = self.api_head('/entity/{id}'.format(id=entity_id), headers={'X-Auth-Token': 'some token value'})

        assert_that(code, equal_to(200))

    def test_entity_head_with_nonexistent_entity(self):
        entity_id = "entity_id"
        self.controller.should_receive('entity_exists') \
            .and_return(False)

        code, result = self.api_head('/entity/{id}'.format(id=entity_id), headers={'X-Auth-Token': 'some token value'})

        assert_that(code, equal_to(404))
