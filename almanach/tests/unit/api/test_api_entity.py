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

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_entries
from hamcrest import has_key
from hamcrest import is_
from voluptuous import Invalid

from almanach.core import exception
from almanach.tests.unit.api import base_api
from almanach.tests.unit.builder import a
from almanach.tests.unit.builder import instance


class ApiEntityTest(base_api.BaseApi):

    def test_update_instance_flavor_for_terminated_instance(self):
        some_new_flavor = 'some_new_flavor'
        data = dict(flavor=some_new_flavor)
        start = '2016-03-01 00:00:00.000000'
        end = '2016-03-03 00:00:00.000000'

        self.entity_ctl.should_receive('update_inactive_entity').with_args(
            instance_id="INSTANCE_ID",
            start=base_api.a_date_matching(start),
            end=base_api.a_date_matching(end),
            flavor=some_new_flavor,
        ).and_return(a(instance().
                       with_id('INSTANCE_ID').
                       with_start(2016, 3, 1, 0, 0, 0).
                       with_end(2016, 3, 3, 0, 0, 0).
                       with_flavor(some_new_flavor)))

        code, result = self.api_put(
            '/entity/instance/INSTANCE_ID',
            headers={'X-Auth-Token': 'some token value'},
            query_string={
                'start': start,
                'end': end,
            },
            data=data,
        )
        assert_that(code, equal_to(200))
        assert_that(result, has_key('entity_id'))
        assert_that(result, has_key('flavor'))
        assert_that(result['flavor'], is_(some_new_flavor))

    def test_update_instance_entity_with_a_new_start_date(self):
        data = {
            "start_date": "2014-01-01 00:00:00.0000",
        }

        self.entity_ctl.should_receive('update_active_instance_entity') \
            .with_args(
            instance_id="INSTANCE_ID",
            start_date=data["start_date"],
        ).and_return(a(instance().with_id('INSTANCE_ID').with_start(2014, 1, 1, 0, 0, 0)))

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

    def test_update_active_instance_entity_with_bad_payload(self):
        instance_id = 'INSTANCE_ID'
        data = {
            'flavor': 'A_FLAVOR',
        }

        self.entity_ctl.should_receive('update_active_instance_entity') \
            .with_args(instance_id=instance_id, **data) \
            .once() \
            .and_raise(ValueError('Expecting object: line 1 column 15 (char 14)'))

        code, result = self.api_put(
                '/entity/instance/INSTANCE_ID',
                data=data,
                headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries({
            "error": 'Invalid parameter or payload'
        }))
        assert_that(code, equal_to(400))

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

        self.entity_ctl.should_receive('update_active_instance_entity') \
            .with_args(instance_id=instance_id, **data) \
            .once() \
            .and_raise(exception.InvalidAttributeException(errors))

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
        self.entity_ctl.should_receive('entity_exists') \
            .and_return(True)

        code, result = self.api_head('/entity/{id}'.format(id=entity_id), headers={'X-Auth-Token': 'some token value'})

        assert_that(code, equal_to(200))

    def test_entity_head_with_nonexistent_entity(self):
        entity_id = "entity_id"
        self.entity_ctl.should_receive('entity_exists') \
            .and_return(False)

        code, result = self.api_head('/entity/{id}'.format(id=entity_id), headers={'X-Auth-Token': 'some token value'})

        assert_that(code, equal_to(404))
