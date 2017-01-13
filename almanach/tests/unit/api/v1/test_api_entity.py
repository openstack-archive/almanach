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

from voluptuous import Invalid

from almanach.core import exception
from almanach.tests.unit.api.v1 import base_api
from almanach.tests.unit.builders.entity import a
from almanach.tests.unit.builders.entity import instance


class TestApiEntity(base_api.BaseApi):

    def test_update_instance_flavor_for_terminated_instance(self):
        some_new_flavor = 'some_new_flavor'
        an_instance = a(instance().
                        with_id('INSTANCE_ID').
                        with_start(2016, 3, 1, 0, 0, 0).
                        with_end(2016, 3, 3, 0, 0, 0).
                        with_flavor(some_new_flavor))
        self.entity_ctl.update_inactive_entity.return_value = an_instance
        data = dict(flavor=some_new_flavor)
        start = '2016-03-01 00:00:00.000000'
        end = '2016-03-03 00:00:00.000000'

        code, result = self.api_put(
            '/entity/instance/INSTANCE_ID',
            headers={'X-Auth-Token': 'some token value'},
            query_string={
                'start': start,
                'end': end,
            },
            data=data,
        )

        self.entity_ctl.update_inactive_entity.assert_called_once_with(
            instance_id="INSTANCE_ID",
            start=base_api.a_date_matching(start),
            end=base_api.a_date_matching(end),
            flavor=some_new_flavor
        )
        self.assertEqual(code, 200)
        self.assertIn('entity_id', result)
        self.assertIn('flavor', result)
        self.assertEqual(result['flavor'], some_new_flavor)

    def test_update_instance_entity_with_a_new_start_date(self):
        data = {
            "start_date": "2014-01-01 00:00:00.0000",
        }
        an_instance = a(instance().with_id('INSTANCE_ID').with_start(2014, 1, 1, 0, 0, 0))
        self.entity_ctl.update_active_instance_entity.return_value = an_instance

        code, result = self.api_put(
            '/entity/instance/INSTANCE_ID',
            headers={'X-Auth-Token': 'some token value'},
            data=data,
        )

        self.entity_ctl.update_active_instance_entity.assert_called_once_with(
            instance_id="INSTANCE_ID",
            start_date=data["start_date"]
        )
        self.assertEqual(code, 200)
        self.assertIn('entity_id', result)
        self.assertIn('start', result)
        self.assertIn('end', result)
        self.assertEqual(result['start'], "2014-01-01 00:00:00+00:00")

    def test_update_active_instance_entity_with_bad_payload(self):
        self.entity_ctl.update_active_instance_entity.side_effect = ValueError(
            'Expecting object: line 1 column 15 (char 14)'
        )
        instance_id = 'INSTANCE_ID'
        data = {
            'flavor': 'A_FLAVOR',
        }

        code, result = self.api_put(
                '/entity/instance/INSTANCE_ID',
                data=data,
                headers={'X-Auth-Token': 'some token value'}
        )

        self.entity_ctl.update_active_instance_entity.assert_called_once_with(instance_id=instance_id, **data)
        self.assertIn("error", result)
        self.assertEqual(result["error"], 'Invalid parameter or payload')
        self.assertEqual(code, 400)

    def test_update_active_instance_entity_with_wrong_attribute_raise_exception(self):
        errors = [
            Invalid(message="error message1", path=["my_attribute1"]),
            Invalid(message="error message2", path=["my_attribute2"]),
        ]
        self.entity_ctl.update_active_instance_entity.side_effect = exception.InvalidAttributeException(errors)

        formatted_errors = {
            "my_attribute1": "error message1",
            "my_attribute2": "error message2",
        }

        instance_id = 'INSTANCE_ID'
        data = {
            'flavor': 'A_FLAVOR',
        }

        code, result = self.api_put(
            '/entity/instance/INSTANCE_ID',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )

        self.entity_ctl.update_active_instance_entity.assert_called_once_with(instance_id=instance_id, **data)
        self.assertIn("error", result)
        self.assertEqual(result['error'], formatted_errors)
        self.assertEqual(code, 400)

    def test_entity_head_with_existing_entity(self):
        self.entity_ctl.entity_exists.return_value = True
        entity_id = "entity_id"

        code, result = self.api_head('/entity/{id}'.format(id=entity_id), headers={'X-Auth-Token': 'some token value'})

        self.entity_ctl.entity_exists.assert_called_once_with(entity_id=entity_id)
        self.assertEqual(code, 200)

    def test_entity_head_with_nonexistent_entity(self):
        self.entity_ctl.entity_exists.return_value = False
        entity_id = "entity_id"

        code, result = self.api_head('/entity/{id}'.format(id=entity_id), headers={'X-Auth-Token': 'some token value'})

        self.entity_ctl.entity_exists.assert_called_once_with(entity_id=entity_id)
        self.assertEqual(code, 404)
