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
from hamcrest import equal_to, assert_that, has_entry, has_item
from retry import retry

from builders import messages
from base_api_testcase import BaseApiTestCase
from helpers.mongo_helper import MongoHelper


class ApiVolumeTest(BaseApiTestCase):

    @classmethod
    def setUpClass(cls):
        cls.setup_volume_type()

    @classmethod
    def tearDownClass(cls):
        MongoHelper().drop_database()

    @classmethod
    def setup_volume_type(cls):
        cls.rabbitMqHelper.push(
                message=messages.get_volume_type_create_sample(volume_type_id=messages.DEFAULT_VOLUME_TYPE,
                                                               volume_type_name=messages.DEFAULT_VOLUME_TYPE),
        )
        cls._wait_until_volume_type_is_created()

    def test_volume_create(self):
        volume_create_query = "{url}/project/{project}/volume"
        project_id = "my_test_project_id"
        volume_id = str(uuid4())
        data = {'volume_id': volume_id,
                'attached_to': [],
                'volume_name': messages.DEFAULT_VOLUME_NAME,
                'volume_type': messages.DEFAULT_VOLUME_TYPE,
                'start': '2016-01-01T18:30:00Z',
                'size': 100}

        response = self.almanachHelper.post(url=volume_create_query, data=data, project=project_id)
        assert_that(response.status_code, equal_to(201))

        list_query = "{url}/project/{project}/volumes?start={start}&end={end}"
        response = self.almanachHelper.get(url=list_query,
                                           project=project_id,
                                           start="2016-01-01 18:29:00.000", end="2016-01-01 18:31:00.000")

        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_item({'entity_id': volume_id,
                                               'attached_to': data['attached_to'],
                                               'end': None,
                                               'name': data['volume_name'],
                                               'entity_type': 'volume',
                                               'last_event': '2016-01-01 18:30:00+00:00',
                                               'volume_type': messages.DEFAULT_VOLUME_TYPE,
                                               'start': '2016-01-01 18:30:00+00:00',
                                               'project_id': project_id,
                                               'size': data['size']}))

    def test_volume_create_bad_date_format(self):
        volume_create_query = "{url}/project/{project}/volume"
        project_id = "my_test_project_id"
        volume_id = str(uuid4())
        data = {'volume_id': volume_id,
                'attached_to': [],
                'volume_name': messages.DEFAULT_VOLUME_NAME,
                'volume_type': messages.DEFAULT_VOLUME_TYPE,
                'start': 'BAD_DATE_FORMAT',
                'size': 100}

        response = self.almanachHelper.post(url=volume_create_query, data=data, project=project_id)

        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                'error',
                'The provided date has an invalid format. Format should be of yyyy-mm-ddThh:mm:ss.msZ, '
                'ex: 2015-01-31T18:24:34.1523Z'
        ))

    def test_volume_create_missing_param(self):
        volume_create_query = "{url}/project/{project}/volume"
        project_id = "my_test_project_id"
        volume_id = str(uuid4())
        data = {'volume_id': volume_id,
                'attached_to': [],
                'volume_name': messages.DEFAULT_VOLUME_NAME,
                'volume_type': messages.DEFAULT_VOLUME_TYPE,
                'size': 100}

        response = self.almanachHelper.post(url=volume_create_query, data=data, project=project_id)

        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                "error",
                "The 'start' param is mandatory for the request you have made."
        ))

    def test_volume_delete(self):
        volume_create_query = "{url}/project/{project}/volume"
        project_id = "my_test_project_id"
        volume_id = str(uuid4())
        create_data = {'volume_id': volume_id,
                       'attached_to': [],
                       'volume_name': messages.DEFAULT_VOLUME_NAME,
                       'volume_type': messages.DEFAULT_VOLUME_TYPE,
                       'start': '2016-01-01T18:30:00Z',
                       'size': 100}

        response = self.almanachHelper.post(url=volume_create_query, data=create_data, project=project_id)
        assert_that(response.status_code, equal_to(201))

        volume_delete_query = "{url}/volume/{volume_id}"
        delete_data = {'date': '2016-01-01T18:50:00Z'}
        response = self.almanachHelper.delete(url=volume_delete_query, data=delete_data, volume_id=volume_id)
        assert_that(response.status_code, equal_to(202))

        list_query = "{url}/project/{project}/volumes?start={start}&end={end}"
        response = self.almanachHelper.get(url=list_query, project=project_id,
                                           start="2016-01-01 18:49:00.000", end="2016-01-01 18:51:00.000")

        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_item({'entity_id': volume_id,
                                               'attached_to': create_data['attached_to'],
                                               'end': '2016-01-01 18:50:00+00:00',
                                               'name': create_data['volume_name'],
                                               'entity_type': 'volume',
                                               'last_event': '2016-01-01 18:50:00+00:00',
                                               'volume_type': messages.DEFAULT_VOLUME_TYPE,
                                               'start': '2016-01-01 18:30:00+00:00',
                                               'project_id': project_id,
                                               'size': create_data['size']}))

    def test_volume_delete_bad_date_format(self):
        volume_delete_query = "{url}/volume/{volume_id}"
        delete_data = {'date': 'A_BAD_DATE'}

        response = self.almanachHelper.delete(url=volume_delete_query, data=delete_data, volume_id="my_test_volume_id")
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                'error',
                'The provided date has an invalid format. Format should be of yyyy-mm-ddThh:mm:ss.msZ, '
                'ex: 2015-01-31T18:24:34.1523Z'
        ))

    def test_volume_delete_missing_param(self):
        instance_delete_query = "{url}/volume/{volume_id}"

        response = self.almanachHelper.delete(url=instance_delete_query, data=dict(), volume_id="my_test_volume_id")
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                "error",
                "The 'date' param is mandatory for the request you have made."
        ))

    def test_volume_resize(self):
        volume_create_query = "{url}/project/{project}/volume"
        project_id = "my_test_project_id"
        volume_id = str(uuid4())
        create_data = {'volume_id': volume_id,
                       'attached_to': [],
                       'volume_name': messages.DEFAULT_VOLUME_NAME,
                       'volume_type': messages.DEFAULT_VOLUME_TYPE,
                       'start': '2016-01-01T18:30:00Z',
                       'size': 100}

        response = self.almanachHelper.post(url=volume_create_query, data=create_data, project=project_id)
        assert_that(response.status_code, equal_to(201))

        resize_data = {'date': '2016-01-01T18:40:00Z',
                       'size': '150'}

        volume_resize_query = "{url}/volume/{volume_id}/resize"
        response = self.almanachHelper.put(url=volume_resize_query, data=resize_data, volume_id=volume_id)
        assert_that(response.status_code, equal_to(200))

        list_query = "{url}/project/{project}/volumes?start={start}&end={end}"
        response = self.almanachHelper.get(url=list_query,
                                           project=project_id,
                                           start="2016-01-01 18:39:00.000",
                                           end="2016-01-01 18:41:00.000")

        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_item({'entity_id': volume_id,
                                               'attached_to': create_data['attached_to'],
                                               'end': None,
                                               'name': create_data['volume_name'],
                                               'entity_type': 'volume',
                                               'last_event': '2016-01-01 18:40:00+00:00',
                                               'volume_type': messages.DEFAULT_VOLUME_TYPE,
                                               'start': '2016-01-01 18:40:00+00:00',
                                               'project_id': project_id,
                                               'size': resize_data['size']}))

    def test_volume_resize_bad_date_format(self):
        volume_resize_query = "{url}/volume/my_test_volume_id/resize"
        resize_data = {'date': 'A_BAD_DATE',
                       'size': '150'}

        response = self.almanachHelper.put(url=volume_resize_query, data=resize_data)
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                'error',
                'The provided date has an invalid format. Format should be of yyyy-mm-ddThh:mm:ss.msZ, '
                'ex: 2015-01-31T18:24:34.1523Z'
        ))

    def test_volume_resize_missing_param(self):
        volume_resize_query = "{url}/volume/my_test_volume_id/resize"
        resize_data = {'size': '250'}

        response = self.almanachHelper.put(url=volume_resize_query, data=resize_data, instance_id="my_instance_id")
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                "error",
                "The 'date' param is mandatory for the request you have made."
        ))

    def test_volume_attach(self):
        instance_create_query = "{url}/project/{project}/instance"
        project_id = "my_test_project_id"
        instance_id = str(uuid4())
        instance_data = {'id': instance_id,
                         'created_at': '2016-01-01T18:30:00Z',
                         'name': 'integration_test_instance_FlavorA',
                         'flavor': 'FlavorA',
                         'os_type': 'Linux',
                         'os_distro': 'Ubuntu',
                         'os_version': '14.04'}

        response = self.almanachHelper.post(url=instance_create_query, data=instance_data, project=project_id)
        assert_that(response.status_code, equal_to(201))

        volume_create_query = "{url}/project/{project}/volume"
        volume_id = str(uuid4())
        volume_data = {'volume_id': volume_id,
                       'attached_to': [],
                       'volume_name': messages.DEFAULT_VOLUME_NAME,
                       'volume_type': messages.DEFAULT_VOLUME_TYPE,
                       'start': '2016-01-01T18:30:30Z',
                       'size': 100}

        response = self.almanachHelper.post(url=volume_create_query, data=volume_data, project=project_id)
        assert_that(response.status_code, equal_to(201))

        attach_data = {'date': '2016-01-01T18:40:00Z', 'attachments': [instance_id]}

        volume_attach_query = "{url}/volume/{volume_id}/attach"
        response = self.almanachHelper.put(url=volume_attach_query, data=attach_data, volume_id=volume_id)
        assert_that(response.status_code, equal_to(200))

        list_query = "{url}/project/{project}/volumes?start={start}&end={end}"
        response = self.almanachHelper.get(url=list_query,
                                           project=project_id,
                                           start="2016-01-01 18:39:00.000",
                                           end="2016-01-01 18:41:00.000")

        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_item({'entity_id': volume_id,
                                               'attached_to': [instance_id],
                                               'end': None,
                                               'name': volume_data['volume_name'],
                                               'entity_type': 'volume',
                                               'last_event': '2016-01-01 18:40:00+00:00',
                                               'volume_type': messages.DEFAULT_VOLUME_TYPE,
                                               'start': '2016-01-01 18:40:00+00:00',
                                               'project_id': project_id,
                                               'size': volume_data['size']}))

    def test_volume_attach_bad_date_format(self):
        volume_attach_query = "{url}/volume/my_test_volume_id/attach"
        attach_data = {'date': 'A_BAD_DATE',
                       'attachments': ['AN_INSTANCE']}

        response = self.almanachHelper.put(url=volume_attach_query, data=attach_data)
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                'error',
                'The provided date has an invalid format. Format should be of yyyy-mm-ddThh:mm:ss.msZ, '
                'ex: 2015-01-31T18:24:34.1523Z'
        ))

    def test_volume_attach_missing_param(self):
        volume_attach_query = "{url}/volume/my_test_volume_id/attach"
        attach_data = {'attachments': ['AN_INSTANCE']}

        response = self.almanachHelper.put(url=volume_attach_query, data=attach_data)
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                "error",
                "The 'date' param is mandatory for the request you have made."
        ))

    def test_volume_detach(self):
        instance_create_query = "{url}/project/{project}/instance"
        project_id = "my_test_project_id"
        instance_id = str(uuid4())
        instance_data = {'id': instance_id,
                         'created_at': '2016-01-01T18:30:00Z',
                         'name': 'integration_test_instance_FlavorA',
                         'flavor': 'FlavorA',
                         'os_type': 'Linux',
                         'os_distro': 'Ubuntu',
                         'os_version': '14.04'}

        response = self.almanachHelper.post(url=instance_create_query, data=instance_data, project=project_id)
        assert_that(response.status_code, equal_to(201))

        volume_create_query = "{url}/project/{project}/volume"
        project_id = "my_test_project_id"
        volume_id = str(uuid4())
        volume_data = {'volume_id': volume_id,
                       'attached_to': [instance_id],
                       'volume_name': messages.DEFAULT_VOLUME_NAME,
                       'volume_type': messages.DEFAULT_VOLUME_TYPE,
                       'start': '2016-01-01T18:30:30Z',
                       'size': 100}

        response = self.almanachHelper.post(url=volume_create_query, data=volume_data, project=project_id)
        assert_that(response.status_code, equal_to(201))

        detach_data = {'date': '2016-01-01T18:40:00Z',
                       'attachments': []}

        volume_detach_query = "{url}/volume/{volume_id}/detach"
        response = self.almanachHelper.put(url=volume_detach_query, data=detach_data, volume_id=volume_id)
        assert_that(response.status_code, equal_to(200))

        list_query = "{url}/project/{project}/volumes?start={start}&end={end}"
        response = self.almanachHelper.get(url=list_query,
                                           project=project_id,
                                           start="2016-01-01 18:39:00.000",
                                           end="2016-01-01 18:41:00.000")

        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), has_item({'entity_id': volume_id,
                                               'attached_to': detach_data['attachments'],
                                               'end': None,
                                               'name': volume_data['volume_name'],
                                               'entity_type': 'volume',
                                               'last_event': '2016-01-01 18:40:00+00:00',
                                               'volume_type': messages.DEFAULT_VOLUME_TYPE,
                                               'start': '2016-01-01 18:40:00+00:00',
                                               'project_id': project_id,
                                               'size': volume_data['size']}))

    def test_volume_detach_bad_date_format(self):
        volume_detach_query = "{url}/volume/my_test_volume_id/detach"
        attach_data = {'date': 'A_BAD_DATE',
                       'attachments': ['AN_INSTANCE']}

        response = self.almanachHelper.put(url=volume_detach_query, data=attach_data)
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                'error',
                'The provided date has an invalid format. Format should be of yyyy-mm-ddThh:mm:ss.msZ, '
                'ex: 2015-01-31T18:24:34.1523Z'
        ))

    def test_volume_detach_missing_param(self):
        volume_detach_query = "{url}/volume/my_test_volume_id/detach"
        attach_data = {'attachments': ['AN_INSTANCE']}

        response = self.almanachHelper.put(url=volume_detach_query, data=attach_data)
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entry(
                "error",
                "The 'date' param is mandatory for the request you have made."
        ))

    def test_volume_type_create(self):
        volume_type_query = "{url}/volume_type"
        volume_type_id = str(uuid4())
        data = dict(
                type_id=volume_type_id,
                type_name=messages.DEFAULT_VOLUME_NAME
        )

        response = self.almanachHelper.post(url=volume_type_query, data=data)
        assert_that(response.status_code, equal_to(201))

        volume_type_get_query = "{url}/volume_type/{volume_type_id}"

        response = self.almanachHelper.get(url=volume_type_get_query, volume_type_id=volume_type_id)
        assert_that(response.status_code, equal_to(200))
        assert_that(response.json(), equal_to({'volume_type_id': data['type_id'],
                                               'volume_type_name': data['type_name']}))

    @classmethod
    @retry(exceptions=AssertionError, delay=10, max_delay=300)
    def _wait_until_volume_type_is_created(cls):
        assert_that(cls._get_volume_types(messages.DEFAULT_VOLUME_TYPE),
                    has_entry("volume_type_id", messages.DEFAULT_VOLUME_TYPE))

    @classmethod
    def _get_volume_types(cls, type_id):
        query = "{url}/volume_type/{type_id}"
        response = cls.almanachHelper.get(url=query, type_id=type_id)
        return response.json()
