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

from almanach.core import exception
from almanach.tests.unit.api.v1 import base_api
from almanach.tests.unit.builders.entity import a
from almanach.tests.unit.builders.entity import volume_type


class TestApiVolumeType(base_api.BaseApi):

    def test_get_volume_types(self):
        self.volume_type_ctl.list_volume_types.return_value = [
            a(volume_type().with_volume_type_name('some_volume_type_name'))
        ]

        code, result = self.api_get('/volume_types', headers={'X-Auth-Token': 'some token value'})

        self.volume_type_ctl.list_volume_types.assert_called_once()
        self.assertEqual(code, 200)
        self.assertEqual(len(result), 1)
        self.assertIn('volume_type_name', result[0])
        self.assertEqual(result[0]['volume_type_name'], 'some_volume_type_name')

    def test_successful_volume_type_create(self):
        data = dict(
            type_id='A_VOLUME_TYPE_ID',
            type_name="A_VOLUME_TYPE_NAME"
        )

        code, result = self.api_post('/volume_type', data=data, headers={'X-Auth-Token': 'some token value'})

        self.volume_type_ctl.create_volume_type.assert_called_once_with(
            volume_type_id=data['type_id'],
            volume_type_name=data['type_name']
        )
        self.assertEqual(code, 201)

    def test_volume_type_create_missing_a_param_returns_bad_request_code(self):
        data = dict(type_name="A_VOLUME_TYPE_NAME")

        code, result = self.api_post('/volume_type', data=data, headers={'X-Auth-Token': 'some token value'})

        self.volume_type_ctl.create_volume_type.assert_not_called()
        self.assertEqual(result["error"], "The 'type_id' param is mandatory for the request you have made.")
        self.assertEqual(code, 400)

    def test_volume_type_delete_with_authentication(self):
        code, result = self.api_delete('/volume_type/A_VOLUME_TYPE_ID', headers={'X-Auth-Token': 'some token value'})

        self.volume_type_ctl.delete_volume_type.assert_called_once_with('A_VOLUME_TYPE_ID')
        self.assertEqual(code, 202)

    def test_volume_type_delete_not_in_database(self):
        self.volume_type_ctl.delete_volume_type.side_effect = exception.AlmanachException("An exception occurred")

        code, result = self.api_delete('/volume_type/A_VOLUME_TYPE_ID', headers={'X-Auth-Token': 'some token value'})

        self.volume_type_ctl.delete_volume_type.assert_called_once_with('A_VOLUME_TYPE_ID')
        self.assertIn("An exception occurred", result["error"])
        self.assertEqual(code, 500)
