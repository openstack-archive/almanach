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

from uuid import uuid4
from hamcrest import assert_that, equal_to, has_entries

from almanach.common.exceptions.date_format_exception import DateFormatException
from tests.api.base_api import BaseApi


class ApiVolumeTest(BaseApi):

    def test_successful_volume_create(self):
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

    def test_successfull_volume_delete(self):
        data = dict(date="DELETE_DATE")

        self.controller.should_receive('delete_volume') \
            .with_args(volume_id="VOLUME_ID",
                       delete_date=data['date']) \
            .once()

        code, result = self.api_delete('/volume/VOLUME_ID', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(202))

    def test_volume_delete_missing_a_param_returns_bad_request_code(self):

        self.controller.should_receive('delete_volume') \
            .never()

        code, result = self.api_delete('/volume/VOLUME_ID', data=dict(), headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries({"error": "The 'date' param is mandatory for the request you have made."}))
        assert_that(code, equal_to(400))

    def test_volume_delete_no_data_bad_request_code(self):
        self.controller.should_receive('delete_volume') \
            .never()

        code, result = self.api_delete('/volume/VOLUME_ID', headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries({"error": "The request you have made must have data. None was given."}))
        assert_that(code, equal_to(400))

    def test_volume_delete_bad_date_format_returns_bad_request_code(self):
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

    def test_successful_volume_resize(self):
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
        data = dict(date="A_DATE")

        self.controller.should_receive('resize_volume') \
            .never()

        code, result = self.api_put('/volume/VOLUME_ID/resize', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries({"error": "The 'size' param is mandatory for the request you have made."}))
        assert_that(code, equal_to(400))

    def test_volume_resize_bad_date_format_returns_bad_request_code(self):
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

    def test_successful_volume_attach(self):
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

    def test_successful_volume_detach(self):
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
