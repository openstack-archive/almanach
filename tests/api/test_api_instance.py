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

from hamcrest import assert_that, equal_to, has_key, has_length, has_entries, is_

from almanach.common.exceptions.date_format_exception import DateFormatException
from tests.builder import instance, a
from tests.api.base_api import BaseApi, a_date_matching


class ApiInstanceTest(BaseApi):

    def test_get_instances(self):
        self.controller.should_receive('list_instances') \
            .with_args('TENANT_ID', a_date_matching("2014-01-01 00:00:00.0000"),
                       a_date_matching("2014-02-01 00:00:00.0000")) \
            .and_return([a(instance().with_id('123'))])

        code, result = self.api_get('/project/TENANT_ID/instances',
                                    query_string={
                                        'start': '2014-01-01 00:00:00.0000',
                                        'end': '2014-02-01 00:00:00.0000'
                                    },
                                    headers={'X-Auth-Token': 'some token value'})

        assert_that(code, equal_to(200))
        assert_that(result, has_length(1))
        assert_that(result[0], has_key('entity_id'))
        assert_that(result[0]['entity_id'], equal_to('123'))

    def test_update_instance_flavor_for_terminated_instance(self):
        some_new_flavor = 'some_new_flavor'
        data = dict(flavor=some_new_flavor)
        start = '2016-03-01 00:00:00.000000'
        end = '2016-03-03 00:00:00.000000'

        self.controller.should_receive('update_inactive_entity') \
            .with_args(
                instance_id="INSTANCE_ID",
                start=a_date_matching(start),
                end=a_date_matching(end),
                flavor=some_new_flavor,
        ).and_return(a(
                instance().
                with_id('INSTANCE_ID').
                with_start(2016, 03, 01, 00, 0, 00).
                with_end(2016, 03, 03, 00, 0, 00).
                with_flavor(some_new_flavor))
        )

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

    def test_successful_instance_create(self):
        self.having_config('auth_private_key', 'some token value')
        data = dict(id="INSTANCE_ID",
                    created_at="CREATED_AT",
                    name="INSTANCE_NAME",
                    flavor="A_FLAVOR",
                    os_type="AN_OS_TYPE",
                    os_distro="A_DISTRIBUTION",
                    os_version="AN_OS_VERSION")

        self.controller.should_receive('create_instance') \
            .with_args(tenant_id="PROJECT_ID",
                       instance_id=data["id"],
                       create_date=data["created_at"],
                       flavor=data['flavor'],
                       os_type=data['os_type'],
                       distro=data['os_distro'],
                       version=data['os_version'],
                       name=data['name'],
                       metadata={}) \
            .once()

        code, result = self.api_post(
                '/project/PROJECT_ID/instance',
                data=data,
                headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(code, equal_to(201))

    def test_instance_create_missing_a_param_returns_bad_request_code(self):
        self.having_config('auth_private_key', 'some token value')
        data = dict(id="INSTANCE_ID",
                    created_at="CREATED_AT",
                    name="INSTANCE_NAME",
                    flavor="A_FLAVOR",
                    os_type="AN_OS_TYPE",
                    os_version="AN_OS_VERSION")

        self.controller.should_receive('create_instance') \
            .never()

        code, result = self.api_post(
                '/project/PROJECT_ID/instance',
                data=data,
                headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries({"error": "The 'os_distro' param is mandatory for the request you have made."}))
        assert_that(code, equal_to(400))

    def test_instance_create_bad_date_format_returns_bad_request_code(self):
        self.having_config('auth_private_key', 'some token value')
        data = dict(id="INSTANCE_ID",
                    created_at="A_BAD_DATE",
                    name="INSTANCE_NAME",
                    flavor="A_FLAVOR",
                    os_type="AN_OS_TYPE",
                    os_distro="A_DISTRIBUTION",
                    os_version="AN_OS_VERSION")

        self.controller.should_receive('create_instance') \
            .with_args(tenant_id="PROJECT_ID",
                       instance_id=data["id"],
                       create_date=data["created_at"],
                       flavor=data['flavor'],
                       os_type=data['os_type'],
                       distro=data['os_distro'],
                       version=data['os_version'],
                       name=data['name'],
                       metadata={}) \
            .once() \
            .and_raise(DateFormatException)

        code, result = self.api_post(
                '/project/PROJECT_ID/instance',
                data=data,
                headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries(
                {
                    "error": "The provided date has an invalid format. "
                             "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z"
                }
        ))
        assert_that(code, equal_to(400))

    def test_successful_instance_resize(self):
        data = dict(date="UPDATED_AT",
                    flavor="A_FLAVOR")

        self.controller.should_receive('resize_instance') \
            .with_args(instance_id="INSTANCE_ID",
                       flavor=data['flavor'],
                       resize_date=data['date']) \
            .once()

        code, result = self.api_put(
                '/instance/INSTANCE_ID/resize',
                data=data,
                headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(code, equal_to(200))

    def test_successfull_instance_delete(self):
        data = dict(date="DELETE_DATE")

        self.controller.should_receive('delete_instance') \
            .with_args(instance_id="INSTANCE_ID",
                       delete_date=data['date']) \
            .once()

        code, result = self.api_delete('/instance/INSTANCE_ID', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(202))

    def test_instance_delete_missing_a_param_returns_bad_request_code(self):
        self.controller.should_receive('delete_instance') \
            .never()

        code, result = self.api_delete(
                '/instance/INSTANCE_ID',
                data=dict(),
                headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries({"error": "The 'date' param is mandatory for the request you have made."}))
        assert_that(code, equal_to(400))

    def test_instance_delete_no_data_bad_request_code(self):
        self.controller.should_receive('delete_instance') \
            .never()

        code, result = self.api_delete('/instance/INSTANCE_ID', headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries({"error": "The request you have made must have data. None was given."}))
        assert_that(code, equal_to(400))

    def test_instance_delete_bad_date_format_returns_bad_request_code(self):
        data = dict(date="A_BAD_DATE")

        self.controller.should_receive('delete_instance') \
            .with_args(instance_id="INSTANCE_ID",
                       delete_date=data['date']) \
            .once() \
            .and_raise(DateFormatException)

        code, result = self.api_delete('/instance/INSTANCE_ID', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries(
                {
                    "error": "The provided date has an invalid format. "
                             "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z"
                }
        ))
        assert_that(code, equal_to(400))

    def test_instance_resize_missing_a_param_returns_bad_request_code(self):
        data = dict(date="UPDATED_AT")

        self.controller.should_receive('resize_instance') \
            .never()

        code, result = self.api_put(
                '/instance/INSTANCE_ID/resize',
                data=data,
                headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries({"error": "The 'flavor' param is mandatory for the request you have made."}))
        assert_that(code, equal_to(400))

    def test_instance_resize_bad_date_format_returns_bad_request_code(self):
        data = dict(date="A_BAD_DATE",
                    flavor="A_FLAVOR")

        self.controller.should_receive('resize_instance') \
            .with_args(instance_id="INSTANCE_ID",
                       flavor=data['flavor'],
                       resize_date=data['date']) \
            .once() \
            .and_raise(DateFormatException)

        code, result = self.api_put(
                '/instance/INSTANCE_ID/resize',
                data=data,
                headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries(
                {
                    "error": "The provided date has an invalid format. "
                             "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z"
                }
        ))
        assert_that(code, equal_to(400))

    def test_rebuild_instance(self):
        instance_id = 'INSTANCE_ID'
        data = {
            'distro': 'A_DISTRIBUTION',
            'version': 'A_VERSION',
            'os_type': 'AN_OS_TYPE',
            'rebuild_date': 'UPDATE_DATE',
        }
        self.controller.should_receive('rebuild_instance') \
            .with_args(
                instance_id=instance_id,
                distro=data.get('distro'),
                version=data.get('version'),
                os_type=data.get('os_type'),
                rebuild_date=data.get('rebuild_date')) \
            .once()

        code, result = self.api_put(
                '/instance/INSTANCE_ID/rebuild',
                data=data,
                headers={'X-Auth-Token': 'some token value'}
        )

        assert_that(code, equal_to(200))

    def test_rebuild_instance_missing_a_param_returns_bad_request_code(self):
        data = {
            'distro': 'A_DISTRIBUTION',
            'rebuild_date': 'UPDATE_DATE',
        }

        self.controller.should_receive('rebuild_instance') \
            .never()

        code, result = self.api_put(
                '/instance/INSTANCE_ID/rebuild',
                data=data,
                headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries({"error": "The 'version' param is mandatory for the request you have made."}))
        assert_that(code, equal_to(400))

    def test_rebuild_instance_bad_date_format_returns_bad_request_code(self):
        instance_id = 'INSTANCE_ID'
        data = {
            'distro': 'A_DISTRIBUTION',
            'version': 'A_VERSION',
            'os_type': 'AN_OS_TYPE',
            'rebuild_date': 'A_BAD_UPDATE_DATE',
        }

        self.controller.should_receive('rebuild_instance') \
            .with_args(instance_id=instance_id, **data) \
            .once() \
            .and_raise(DateFormatException)

        code, result = self.api_put(
                '/instance/INSTANCE_ID/rebuild',
                data=data,
                headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries(
                {
                    "error": "The provided date has an invalid format. "
                             "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z"
                }
        ))
