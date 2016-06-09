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

from hamcrest import assert_that, equal_to, has_entries, has_length, has_key, has_entry

from almanach.common.exceptions.almanach_exception import AlmanachException
from tests.builder import volume_type, a
from tests.api.base_api import BaseApi


class ApiVolumeTypeTest(BaseApi):

    def test_get_volume_types(self):
        self.controller.should_receive('list_volume_types') \
            .and_return([a(volume_type().with_volume_type_name('some_volume_type_name'))]) \
            .once()

        code, result = self.api_get('/volume_types', headers={'X-Auth-Token': 'some token value'})

        assert_that(code, equal_to(200))
        assert_that(result, has_length(1))
        assert_that(result[0], has_key('volume_type_name'))
        assert_that(result[0]['volume_type_name'], equal_to('some_volume_type_name'))

    def test_successful_volume_type_create(self):
        data = dict(
                type_id='A_VOLUME_TYPE_ID',
                type_name="A_VOLUME_TYPE_NAME"
        )

        self.controller.should_receive('create_volume_type') \
            .with_args(
                volume_type_id=data['type_id'],
                volume_type_name=data['type_name']) \
            .once()

        code, result = self.api_post('/volume_type', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(201))

    def test_volume_type_create_missing_a_param_returns_bad_request_code(self):
        data = dict(type_name="A_VOLUME_TYPE_NAME")

        self.controller.should_receive('create_volume_type') \
            .never()

        code, result = self.api_post('/volume_type', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(400))
        assert_that(result, has_entries({"error": "The 'type_id' param is mandatory for the request you have made."}))

    def test_volume_type_delete_with_authentication(self):
        self.controller.should_receive('delete_volume_type') \
            .with_args('A_VOLUME_TYPE_ID') \
            .once()

        code, result = self.api_delete('/volume_type/A_VOLUME_TYPE_ID', headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(202))

    def test_volume_type_delete_not_in_database(self):
        self.controller.should_receive('delete_volume_type') \
            .with_args('A_VOLUME_TYPE_ID') \
            .and_raise(AlmanachException("An exception occurred")) \
            .once()

        code, result = self.api_delete('/volume_type/A_VOLUME_TYPE_ID', headers={'X-Auth-Token': 'some token value'})

        assert_that(code, equal_to(500))
        assert_that(result, has_entry("error", "An exception occurred"))
