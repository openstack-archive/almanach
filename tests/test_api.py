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

import json
from uuid import uuid4
from unittest import TestCase
from datetime import datetime

import flask
from voluptuous import Invalid

from flexmock import flexmock, flexmock_teardown

from hamcrest import assert_that, has_key, equal_to, has_length, has_entry, has_entries, is_

from almanach.common.exceptions.validation_exception import InvalidAttributeException
from almanach import config
from almanach.common.exceptions.date_format_exception import DateFormatException
from almanach.common.exceptions.almanach_exception import AlmanachException
from almanach.adapters import api_route_v1 as api_route
from tests.builder import a, instance, volume_type


class ApiTest(TestCase):
    def setUp(self):
        self.controller = flexmock()
        api_route.controller = self.controller

        self.app = flask.Flask("almanach")
        self.app.register_blueprint(api_route.api)

    def tearDown(self):
        flexmock_teardown()

    def test_info(self):
        self.controller.should_receive('get_application_info').and_return({
            'info': {'version': '1.0'},
            'database': {'all_entities': 10,
                         'active_entities': 2}
        })

        code, result = self.api_get('/info')

        assert_that(code, equal_to(200))
        assert_that(result, has_key('info'))
        assert_that(result['info']['version'], equal_to('1.0'))

    def test_instances_with_authentication(self):
        self.having_config('api_auth_token', 'some token value')
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

        self.having_config('api_auth_token', 'some token value')

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

    def test_update_instance_entity_with_a_new_start_date(self):
        data = {
            "start_date": "2014-01-01 00:00:00.0000",
        }

        self.having_config('api_auth_token', 'some token value')

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

    def test_instances_with_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('list_instances').never()

        code, result = self.api_get('/project/TENANT_ID/instances',
                                    query_string={
                                        'start': '2014-01-01 00:00:00.0000',
                                        'end': '2014-02-01 00:00:00.0000'
                                    },
                                    headers={'X-Auth-Token': 'oops'})

        assert_that(code, equal_to(401))

    def test_instances_without_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('list_instances').never()

        code, result = self.api_get('/project/TENANT_ID/instances',
                                    query_string={
                                        'start': '2014-01-01 00:00:00.0000',
                                        'end': '2014-02-01 00:00:00.0000'
                                    })

        assert_that(code, equal_to(401))

    def test_volumes_with_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('list_volumes').never()

        code, result = self.api_get('/project/TENANT_ID/volumes',
                                    query_string={
                                        'start': '2014-01-01 00:00:00.0000',
                                        'end': '2014-02-01 00:00:00.0000'
                                    },
                                    headers={'X-Auth-Token': 'oops'})

        assert_that(code, equal_to(401))

    def test_entities_with_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('list_entities').never()

        code, result = self.api_get('/project/TENANT_ID/entities',
                                    query_string={
                                        'start': '2014-01-01 00:00:00.0000',
                                        'end': '2014-02-01 00:00:00.0000'
                                    },
                                    headers={'X-Auth-Token': 'oops'})

        assert_that(code, equal_to(401))

    def test_volume_type_with_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('get_volume_type') \
            .with_args('A_VOLUME_TYPE_ID') \
            .and_return([a(volume_type().with_volume_type_id('A_VOLUME_TYPE_ID')
                           .with_volume_type_name('some_volume_type_name'))]) \
            .once()

        code, result = self.api_get('/volume_type/A_VOLUME_TYPE_ID', headers={'X-Auth-Token': 'some token value'})

        assert_that(code, equal_to(200))
        assert_that(result, has_length(1))
        assert_that(result[0], has_key('volume_type_id'))
        assert_that(result[0]['volume_type_id'], equal_to('A_VOLUME_TYPE_ID'))
        assert_that(result[0], has_key('volume_type_name'))
        assert_that(result[0]['volume_type_name'], equal_to('some_volume_type_name'))

    def test_volume_type_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('get_volume_type').never()

        code, result = self.api_get('/volume_type/A_VOLUME_TYPE_ID', headers={'X-Auth-Token': 'oops'})
        assert_that(code, equal_to(401))

    def test_volume_types_with_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('list_volume_types') \
            .and_return([a(volume_type().with_volume_type_name('some_volume_type_name'))]) \
            .once()

        code, result = self.api_get('/volume_types', headers={'X-Auth-Token': 'some token value'})

        assert_that(code, equal_to(200))
        assert_that(result, has_length(1))
        assert_that(result[0], has_key('volume_type_name'))
        assert_that(result[0]['volume_type_name'], equal_to('some_volume_type_name'))

    def test_volume_types_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('list_volume_types').never()

        code, result = self.api_get('/volume_types', headers={'X-Auth-Token': 'oops'})
        assert_that(code, equal_to(401))

    def test_successful_volume_type_create(self):
        self.having_config('api_auth_token', 'some token value')
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
        self.having_config('api_auth_token', 'some token value')
        data = dict(type_name="A_VOLUME_TYPE_NAME")

        self.controller.should_receive('create_volume_type') \
            .never()

        code, result = self.api_post('/volume_type', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(400))
        assert_that(result, has_entries({"error": "The 'type_id' param is mandatory for the request you have made."}))

    def test_volume_type_create_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('create_volume_type').never()

        code, result = self.api_post('/volume_type', headers={'X-Auth-Token': 'oops'})
        assert_that(code, equal_to(401))

    def test_volume_type_delete_with_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('delete_volume_type') \
            .with_args('A_VOLUME_TYPE_ID') \
            .once()

        code, result = self.api_delete('/volume_type/A_VOLUME_TYPE_ID', headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(202))

    def test_volume_type_delete_not_in_database(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('delete_volume_type') \
            .with_args('A_VOLUME_TYPE_ID') \
            .and_raise(AlmanachException("An exception occurred")) \
            .once()

        code, result = self.api_delete('/volume_type/A_VOLUME_TYPE_ID', headers={'X-Auth-Token': 'some token value'})

        assert_that(code, equal_to(500))
        assert_that(result, has_entry("error", "An exception occurred"))

    def test_volume_type_delete_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('delete_volume_type').never()

        code, result = self.api_delete('/volume_type/A_VOLUME_TYPE_ID', headers={'X-Auth-Token': 'oops'})
        assert_that(code, equal_to(401))

    def test_successful_volume_create(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(volume_id="VOLUME_ID",
                    start="START_DATE",
                    volume_type="VOLUME_TYPE",
                    size="A_SIZE",
                    volume_name="VOLUME_NAME",
                    attached_to=["INSTANCE_ID"])

        self.controller.should_receive('create_volume') \
            .with_args(project_id="PROJECT_ID",
                       **data) \
            .once()

        code, result = self.api_post(
            '/project/PROJECT_ID/volume',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(code, equal_to(201))

    def test_volume_create_missing_a_param_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(volume_id="VOLUME_ID",
                    start="START_DATE",
                    size="A_SIZE",
                    volume_name="VOLUME_NAME",
                    attached_to=[])

        self.controller.should_receive('create_volume') \
            .never()

        code, result = self.api_post(
            '/project/PROJECT_ID/volume',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(
            result,
            has_entries({"error": "The 'volume_type' param is mandatory for the request you have made."})
        )
        assert_that(code, equal_to(400))

    def test_volume_create_bad_date_format_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(volume_id="VOLUME_ID",
                    start="A_BAD_DATE",
                    volume_type="VOLUME_TYPE",
                    size="A_SIZE",
                    volume_name="VOLUME_NAME",
                    attached_to=["INSTANCE_ID"])

        self.controller.should_receive('create_volume') \
            .with_args(project_id="PROJECT_ID",
                       **data) \
            .once() \
            .and_raise(DateFormatException)

        code, result = self.api_post(
            '/project/PROJECT_ID/volume',
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

    def test_volume_create_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('create_volume').never()

        code, result = self.api_post('/project/PROJECT_ID/volume', headers={'X-Auth-Token': 'oops'})
        assert_that(code, equal_to(401))

    def test_successfull_volume_delete(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(date="DELETE_DATE")

        self.controller.should_receive('delete_volume') \
            .with_args(volume_id="VOLUME_ID",
                       delete_date=data['date']) \
            .once()

        code, result = self.api_delete('/volume/VOLUME_ID', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(202))

    def test_volume_delete_missing_a_param_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')

        self.controller.should_receive('delete_volume') \
            .never()

        code, result = self.api_delete('/volume/VOLUME_ID', data=dict(), headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries({"error": "The 'date' param is mandatory for the request you have made."}))
        assert_that(code, equal_to(400))

    def test_volume_delete_no_data_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')

        self.controller.should_receive('delete_volume') \
            .never()

        code, result = self.api_delete('/volume/VOLUME_ID', headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries({"error": "The request you have made must have data. None was given."}))
        assert_that(code, equal_to(400))

    def test_volume_delete_bad_date_format_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(date="A_BAD_DATE")

        self.controller.should_receive('delete_volume') \
            .with_args(volume_id="VOLUME_ID",
                       delete_date=data['date']) \
            .once() \
            .and_raise(DateFormatException)

        code, result = self.api_delete('/volume/VOLUME_ID', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries(
            {
                "error": "The provided date has an invalid format. "
                         "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z"
            }
        ))
        assert_that(code, equal_to(400))

    def test_volume_delete_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('delete_volume').never()

        code, result = self.api_delete('/volume/VOLUME_ID', headers={'X-Auth-Token': 'oops'})
        assert_that(code, equal_to(401))

    def test_successful_volume_resize(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(date="UPDATED_AT",
                    size="NEW_SIZE")

        self.controller.should_receive('resize_volume') \
            .with_args(volume_id="VOLUME_ID",
                       size=data['size'],
                       update_date=data['date']) \
            .once()

        code, result = self.api_put('/volume/VOLUME_ID/resize', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(200))

    def test_volume_resize_missing_a_param_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(date="A_DATE")

        self.controller.should_receive('resize_volume') \
            .never()

        code, result = self.api_put('/volume/VOLUME_ID/resize', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries({"error": "The 'size' param is mandatory for the request you have made."}))
        assert_that(code, equal_to(400))

    def test_volume_resize_bad_date_format_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(date="BAD_DATE",
                    size="NEW_SIZE")

        self.controller.should_receive('resize_volume') \
            .with_args(volume_id="VOLUME_ID",
                       size=data['size'],
                       update_date=data['date']) \
            .once() \
            .and_raise(DateFormatException)

        code, result = self.api_put('/volume/VOLUME_ID/resize', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries(
            {
                "error": "The provided date has an invalid format. "
                         "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z"
            }
        ))
        assert_that(code, equal_to(400))

    def test_volume_resize_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('resize_volume').never()

        code, result = self.api_put('/volume/INSTANCE_ID/resize', headers={'X-Auth-Token': 'oops'})
        assert_that(code, equal_to(401))

    def test_successful_volume_attach(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(date="UPDATED_AT",
                    attachments=[str(uuid4())])

        self.controller.should_receive('attach_volume') \
            .with_args(volume_id="VOLUME_ID",
                       attachments=data['attachments'],
                       date=data['date']) \
            .once()

        code, result = self.api_put('/volume/VOLUME_ID/attach', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(200))

    def test_volume_attach_missing_a_param_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(date="A_DATE")

        self.controller.should_receive('attach_volume') \
            .never()

        code, result = self.api_put(
            '/volume/VOLUME_ID/attach',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(
            result,
            has_entries({"error": "The 'attachments' param is mandatory for the request you have made."})
        )
        assert_that(code, equal_to(400))

    def test_volume_attach_bad_date_format_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(date="A_BAD_DATE",
                    attachments=[str(uuid4())])

        self.controller.should_receive('attach_volume') \
            .with_args(volume_id="VOLUME_ID",
                       attachments=data['attachments'],
                       date=data['date']) \
            .once() \
            .and_raise(DateFormatException)

        code, result = self.api_put('/volume/VOLUME_ID/attach', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries(
            {
                "error": "The provided date has an invalid format. "
                         "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z"
            }
        ))
        assert_that(code, equal_to(400))

    def test_volume_attach_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('attach_volume').never()

        code, result = self.api_put('/volume/INSTANCE_ID/attach', headers={'X-Auth-Token': 'oops'})
        assert_that(code, equal_to(401))

    def test_successful_volume_detach(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(date="UPDATED_AT",
                    attachments=[str(uuid4())])

        self.controller.should_receive('detach_volume') \
            .with_args(volume_id="VOLUME_ID",
                       attachments=data['attachments'],
                       date=data['date']) \
            .once()

        code, result = self.api_put('/volume/VOLUME_ID/detach', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(200))

    def test_volume_detach_missing_a_param_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(date="A_DATE")

        self.controller.should_receive('detach_volume') \
            .never()

        code, result = self.api_put('/volume/VOLUME_ID/detach', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(
            result,
            has_entries({"error": "The 'attachments' param is mandatory for the request you have made."})
        )
        assert_that(code, equal_to(400))

    def test_volume_detach_bad_date_format_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')
        data = dict(date="A_BAD_DATE",
                    attachments=[str(uuid4())])

        self.controller.should_receive('detach_volume') \
            .with_args(volume_id="VOLUME_ID",
                       attachments=data['attachments'],
                       date=data['date']) \
            .once() \
            .and_raise(DateFormatException)

        code, result = self.api_put('/volume/VOLUME_ID/detach', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries(
            {
                "error": "The provided date has an invalid format. "
                         "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z"
            }
        ))
        assert_that(code, equal_to(400))

    def test_volume_detach_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('detach_volume').never()

        code, result = self.api_put('/volume/INSTANCE_ID/detach', headers={'X-Auth-Token': 'oops'})
        assert_that(code, equal_to(401))

    def test_successful_instance_create(self):
        self.having_config('api_auth_token', 'some token value')
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
        self.having_config('api_auth_token', 'some token value')
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
        self.having_config('api_auth_token', 'some token value')
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

    def test_instance_create_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('create_instance').never()

        code, result = self.api_post('/project/PROJECT_ID/instance', headers={'X-Auth-Token': 'oops'})

        assert_that(code, equal_to(401))

    def test_successful_instance_resize(self):
        self.having_config('api_auth_token', 'some token value')
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
        self.having_config('api_auth_token', 'some token value')
        data = dict(date="DELETE_DATE")

        self.controller.should_receive('delete_instance') \
            .with_args(instance_id="INSTANCE_ID",
                       delete_date=data['date']) \
            .once()

        code, result = self.api_delete('/instance/INSTANCE_ID', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(202))

    def test_instance_delete_missing_a_param_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')

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
        self.having_config('api_auth_token', 'some token value')

        self.controller.should_receive('delete_instance') \
            .never()

        code, result = self.api_delete('/instance/INSTANCE_ID', headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries({"error": "The request you have made must have data. None was given."}))
        assert_that(code, equal_to(400))

    def test_instance_delete_bad_date_format_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')
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

    def test_instance_delete_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('delete_instance').never()

        code, result = self.api_delete('/instance/INSTANCE_ID', headers={'X-Auth-Token': 'oops'})
        assert_that(code, equal_to(401))

    def test_instance_resize_missing_a_param_returns_bad_request_code(self):
        self.having_config('api_auth_token', 'some token value')
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
        self.having_config('api_auth_token', 'some token value')
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

    def test_instance_resize_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('resize_instance').never()

        code, result = self.api_put('/instance/INSTANCE_ID/resize', headers={'X-Auth-Token': 'oops'})
        assert_that(code, equal_to(401))

    def test_rebuild_instance(self):
        self.having_config('api_auth_token', 'some token value')
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
        self.having_config('api_auth_token', 'some token value')
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
        self.having_config('api_auth_token', 'some token value')
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
        assert_that(code, equal_to(400))

    def test_rebuild_instance_wrong_authentication(self):
        self.having_config('api_auth_token', 'some token value')
        self.controller.should_receive('rebuild_instance').never()

        code, result = self.api_put('/instance/INSTANCE_ID/rebuild', headers={'X-Auth-Token': 'oops'})
        assert_that(code, equal_to(401))

    def api_get(self, url, query_string=None, headers=None, accept='application/json'):
        return self._api_call(url, "get", None, query_string, headers, accept)

    def api_post(self, url, data=None, query_string=None, headers=None, accept='application/json'):
        return self._api_call(url, "post", data, query_string, headers, accept)

    def api_put(self, url, data=None, query_string=None, headers=None, accept='application/json'):
        return self._api_call(url, "put", data, query_string, headers, accept)

    def api_delete(self, url, query_string=None, data=None, headers=None, accept='application/json'):
        return self._api_call(url, "delete", data, query_string, headers, accept)

    def _api_call(self, url, method, data=None, query_string=None, headers=None, accept='application/json'):
        with self.app.test_client() as http_client:
            if not headers:
                headers = {}
        headers['Accept'] = accept
        result = getattr(http_client, method)(url, data=json.dumps(data), query_string=query_string, headers=headers)
        return_data = json.loads(result.data) \
            if result.headers.get('Content-Type') == 'application/json' \
            else result.data
        return result.status_code, return_data

    @staticmethod
    def having_config(key, value):
        (flexmock(config)
         .should_receive(key)
         .and_return(value))

    def test_update_active_instance_entity_with_wrong_attribute_exception(self):
        errors = [
            Invalid(message="error message1", path=["my_attribute1"]),
            Invalid(message="error message2", path=["my_attribute2"]),
        ]

        formatted_errors = {
            "my_attribute1": "error message1",
            "my_attribute2": "error message2",
        }

        self.having_config('api_auth_token', 'some token value')
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


class DateMatcher(object):
    def __init__(self, date):
        self.date = date

    def __eq__(self, other):
        return other == self.date


def a_date_matching(date_string):
    return DateMatcher(datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f"))
