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
from almanach.tests.unit.builders.entity import instance


class TestApiInstance(base_api.BaseApi):

    def test_get_instances(self):
        self.instance_ctl.list_instances.return_value = [a(instance().with_id('123'))]
        code, result = self.api_get('/project/TENANT_ID/instances',
                                    query_string={
                                        'start': '2014-01-01 00:00:00.0000',
                                        'end': '2014-02-01 00:00:00.0000'
                                    },
                                    headers={'X-Auth-Token': 'some token value'})

        self.instance_ctl.list_instances.assert_called_once_with(
            'TENANT_ID', base_api.a_date_matching("2014-01-01 00:00:00.0000"),
            base_api.a_date_matching("2014-02-01 00:00:00.0000")
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(result), 1)
        self.assertIn('entity_id', result[0])
        self.assertEqual(result[0]['entity_id'], '123')

    def test_successful_instance_create(self):
        data = dict(id="INSTANCE_ID",
                    created_at="CREATED_AT",
                    name="INSTANCE_NAME",
                    flavor="A_FLAVOR",
                    os_type="AN_OS_TYPE",
                    os_distro="A_DISTRIBUTION",
                    os_version="AN_OS_VERSION")

        code, result = self.api_post(
            '/project/PROJECT_ID/instance',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )

        self.instance_ctl.create_instance.assert_called_once_with(
            tenant_id="PROJECT_ID",
            instance_id=data["id"],
            create_date=data["created_at"],
            name=data['name'],
            flavor=data['flavor'],
            image_meta=dict(os_type=data['os_type'],
                            distro=data['os_distro'],
                            version=data['os_version'])
        )
        self.assertEqual(code, 201)

    def test_instance_create_missing_a_param_returns_bad_request_code(self):
        data = dict(id="INSTANCE_ID",
                    created_at="CREATED_AT",
                    name="INSTANCE_NAME",
                    flavor="A_FLAVOR",
                    os_type="AN_OS_TYPE",
                    os_version="AN_OS_VERSION")

        code, result = self.api_post(
            '/project/PROJECT_ID/instance',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )

        self.instance_ctl.create_instance.assert_not_called()
        self.assertEqual(result["error"], "The 'os_distro' param is mandatory for the request you have made.")
        self.assertEqual(code, 400)

    def test_instance_create_bad_date_format_returns_bad_request_code(self):
        self.instance_ctl.create_instance.side_effect = exception.DateFormatException
        data = dict(id="INSTANCE_ID",
                    created_at="A_BAD_DATE",
                    name="INSTANCE_NAME",
                    flavor="A_FLAVOR",
                    os_type="AN_OS_TYPE",
                    os_distro="A_DISTRIBUTION",
                    os_version="AN_OS_VERSION")

        code, result = self.api_post(
            '/project/PROJECT_ID/instance',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )

        self.instance_ctl.create_instance.assert_called_once_with(
            tenant_id="PROJECT_ID",
            instance_id=data["id"],
            create_date=data["created_at"],
            flavor=data['flavor'],
            image_meta=dict(os_type=data['os_type'],
                            distro=data['os_distro'],
                            version=data['os_version']),
            name=data['name']
        )

        self.assertIn(
            "The provided date has an invalid format. "
            "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z",
            result["error"]
        )
        self.assertEqual(code, 400)

    def test_successful_instance_resize(self):
        data = dict(date="UPDATED_AT",
                    flavor="A_FLAVOR")

        code, result = self.api_put(
            '/instance/INSTANCE_ID/resize',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )

        self.instance_ctl.resize_instance.assert_called_once_with(
            instance_id="INSTANCE_ID",
            flavor=data['flavor'],
            resize_date=data['date']
        )
        self.assertEqual(code, 200)

    def test_successfull_instance_delete(self):
        data = dict(date="DELETE_DATE")

        code, result = self.api_delete('/instance/INSTANCE_ID', data=data, headers={'X-Auth-Token': 'some token value'})

        self.instance_ctl.delete_instance.assert_called_once_with(
            instance_id="INSTANCE_ID",
            delete_date=data['date']
        )
        self.assertEqual(code, 202)

    def test_instance_delete_missing_a_param_returns_bad_request_code(self):
        code, result = self.api_delete(
            '/instance/INSTANCE_ID',
            data=dict(),
            headers={'X-Auth-Token': 'some token value'}
        )

        self.instance_ctl.delete_instance.assert_not_called()
        self.assertIn(
            "The 'date' param is mandatory for the request you have made.",
            result["error"]
        )
        self.assertEqual(code, 400)

    def test_instance_delete_no_data_bad_request_code(self):
        code, result = self.api_delete('/instance/INSTANCE_ID', headers={'X-Auth-Token': 'some token value'})

        self.instance_ctl.delete_instance.assert_not_called()
        self.assertIn(
            "Invalid parameter or payload",
            result["error"]
        )
        self.assertEqual(code, 400)

    def test_instance_delete_bad_date_format_returns_bad_request_code(self):
        data = dict(date="A_BAD_DATE")
        self.instance_ctl.delete_instance.side_effect = exception.DateFormatException

        code, result = self.api_delete('/instance/INSTANCE_ID', data=data, headers={'X-Auth-Token': 'some token value'})

        self.instance_ctl.delete_instance.assert_called_once_with(
            instance_id="INSTANCE_ID",
            delete_date=data['date']
        )
        self.assertIn(
            "The provided date has an invalid format. "
            "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z",
            result["error"]
        )
        self.assertEqual(code, 400)

    def test_instance_resize_missing_a_param_returns_bad_request_code(self):
        data = dict(date="UPDATED_AT")
        code, result = self.api_put(
            '/instance/INSTANCE_ID/resize',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )

        self.instance_ctl.resize_instance.assert_not_called()
        self.assertIn(
            "The 'flavor' param is mandatory for the request you have made.",
            result["error"]
        )
        self.assertEqual(code, 400)

    def test_instance_resize_bad_date_format_returns_bad_request_code(self):
        self.instance_ctl.resize_instance.side_effect = exception.DateFormatException
        data = dict(date="A_BAD_DATE",
                    flavor="A_FLAVOR")
        code, result = self.api_put(
            '/instance/INSTANCE_ID/resize',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )

        self.instance_ctl.resize_instance.assert_called_once_with(
            instance_id="INSTANCE_ID",
            flavor=data['flavor'],
            resize_date=data['date']
        )
        self.assertIn(
            "The provided date has an invalid format. "
            "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z",
            result["error"]
        )
        self.assertEqual(code, 400)

    def test_rebuild_instance(self):
        instance_id = 'INSTANCE_ID'
        data = {
            'distro': 'A_DISTRIBUTION',
            'version': 'A_VERSION',
            'os_type': 'AN_OS_TYPE',
            'rebuild_date': 'UPDATE_DATE',
        }
        code, result = self.api_put(
            '/instance/INSTANCE_ID/rebuild',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )

        self.instance_ctl.rebuild_instance.assert_called_once_with(
            instance_id=instance_id,
            rebuild_date=data.get('rebuild_date'),
            image_meta=dict(distro=data.get('distro'),
                            version=data.get('version'),
                            os_type=data.get('os_type'))
        )
        self.assertEqual(code, 200)

    def test_rebuild_instance_missing_a_param_returns_bad_request_code(self):
        data = {
            'distro': 'A_DISTRIBUTION',
            'rebuild_date': 'UPDATE_DATE',
        }
        code, result = self.api_put(
            '/instance/INSTANCE_ID/rebuild',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )

        self.instance_ctl.rebuild_instance.assert_not_called()
        self.assertIn(
            "The 'version' param is mandatory for the request you have made.",
            result["error"]
        )
        self.assertEqual(code, 400)

    def test_rebuild_instance_bad_date_format_returns_bad_request_code(self):
        self.instance_ctl.rebuild_instance.side_effect = exception.DateFormatException
        instance_id = 'INSTANCE_ID'
        data = {
            'distro': 'A_DISTRIBUTION',
            'version': 'A_VERSION',
            'os_type': 'AN_OS_TYPE',
            'rebuild_date': 'A_BAD_UPDATE_DATE',
        }
        code, result = self.api_put(
            '/instance/INSTANCE_ID/rebuild',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )

        self.instance_ctl.rebuild_instance.assert_called_once_with(
            instance_id=instance_id,
            rebuild_date=data.get('rebuild_date'),
            image_meta=dict(distro=data.get('distro'),
                            version=data.get('version'),
                            os_type=data.get('os_type'))
        )
        self.assertIn(
            "The provided date has an invalid format. "
            "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z",
            result["error"]
        )
        self.assertEqual(code, 400)
