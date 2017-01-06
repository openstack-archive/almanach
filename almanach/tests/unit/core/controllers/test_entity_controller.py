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

from copy import copy
from datetime import datetime
from dateutil.parser import parse
import mock
import pytz

from almanach.core.controllers import entity_controller
from almanach.core import exception
from almanach.storage.drivers import base_driver

from almanach.tests.unit import base
from almanach.tests.unit.builders.entity import a
from almanach.tests.unit.builders.entity import instance


class TestEntityController(base.BaseTestCase):

    def setUp(self):
        super(TestEntityController, self).setUp()
        self.database_adapter = mock.Mock(spec=base_driver.BaseDriver)
        self.controller = entity_controller.EntityController(self.database_adapter)

    def test_update_active_instance_entity_with_a_new_flavor(self):
        flavor = u"my flavor name"
        fake_instance1 = a(instance())
        fake_instance2 = copy(fake_instance1)

        self.controller.update_active_instance_entity(
            instance_id=fake_instance1.entity_id,
            flavor=flavor,
        )

        self._expect_get_active_entity_and_update(fake_instance1, fake_instance2, flavor=flavor)

    def test_update_active_instance_entity_with_a_new_name(self):
        name = u"my instance name"
        fake_instance1 = a(instance())
        fake_instance2 = copy(fake_instance1)

        self.controller.update_active_instance_entity(
            instance_id=fake_instance1.entity_id,
            name=name,
        )

        self._expect_get_active_entity_and_update(fake_instance1, fake_instance2, name=name)

    def test_update_active_instance_entity_with_a_new_os(self):
        os = {
            "os_type": u"linux",
            "version": u"7",
            "distro": u"centos"
        }
        fake_instance1 = a(instance())
        fake_instance2 = copy(fake_instance1)

        self.controller.update_active_instance_entity(
            instance_id=fake_instance1.entity_id,
            os=os,
        )

        self._expect_get_active_entity_and_update(fake_instance1, fake_instance2, os=os)

    def test_update_active_instance_entity_with_a_new_metadata(self):
        metadata = {
            "key": "value"
        }
        fake_instance1 = a(instance())
        fake_instance2 = copy(fake_instance1)

        self.controller.update_active_instance_entity(
            instance_id=fake_instance1.entity_id,
            metadata=metadata,
        )

        self._expect_get_active_entity_and_update(fake_instance1, fake_instance2, metadata=metadata)

    def test_update_active_instance_entity_with_a_new_start_date(self):
        fake_instance1 = a(instance())
        fake_instance2 = copy(fake_instance1)

        self.controller.update_active_instance_entity(
            instance_id=fake_instance1.entity_id,
            start_date="2015-10-21T16:25:00.000000Z",
        )

        self._expect_get_active_entity_and_update(fake_instance1, fake_instance2, start="2015-10-21T16:25:00.000000Z")

    def test_update_active_instance_entity_with_a_new_end_date(self):
        fake_instance1 = a(instance())
        fake_instance2 = copy(fake_instance1)

        self.controller.update_active_instance_entity(
            instance_id=fake_instance1.entity_id,
            end_date="2015-10-21T16:25:00.000000Z",
        )

        self._expect_get_active_entity_and_update(fake_instance1, fake_instance2, end="2015-10-21T16:25:00.000000Z")

    def test_update_entity_closed_entity_flavor(self):
        start = datetime(2016, 3, 1, 0, 0, 0, 0, pytz.utc)
        end = datetime(2016, 3, 3, 0, 0, 0, 0, pytz.utc)
        flavor = 'a_new_flavor'
        fake_instance1 = a(instance().with_start(2016, 3, 1, 0, 0, 0).with_end(2016, 3, 2, 0, 0, 0))
        self.database_adapter.get_all_entities_by_id_and_date.side_effect = [[fake_instance1], [fake_instance1]]
        calls = [
            mock.call(fake_instance1.entity_id, start, end),
            mock.call(fake_instance1.entity_id, start, end)
        ]

        self.controller.update_inactive_entity(
            instance_id=fake_instance1.entity_id,
            start=start,
            end=end,
            flavor=flavor,
        )

        self.database_adapter.get_all_entities_by_id_and_date.assert_has_calls(calls)
        self.database_adapter.update_closed_entity.expect_called_once_with(
            entity=fake_instance1, data={"flavor": flavor}
        )

    def test_update_one_closed_entity_return_multiple_entities(self):
        fake_instances = [a(instance()), a(instance())]
        self.database_adapter.get_all_entities_by_id_and_date.return_value = fake_instances

        self.assertRaises(exception.MultipleEntitiesMatchingQueryException,
                          self.controller.update_inactive_entity,
                          instance_id=fake_instances[0].entity_id,
                          start=fake_instances[0].start,
                          end=fake_instances[0].end,
                          flavor=fake_instances[0].flavor)

        self.database_adapter.get_all_entities_by_id_and_date.expect_called_once_with(
            fake_instances[0].entity_id, fake_instances[0].start, fake_instances[0].end
        )

    def test_update_one_closed_entity_return_no_entity(self):
        fake_instance = a(instance())
        self.database_adapter.get_all_entities_by_id_and_date.return_value = []

        self.assertRaises(exception.EntityNotFoundException,
                          self.controller.update_inactive_entity,
                          instance_id=fake_instance.entity_id,
                          start=fake_instance.start,
                          end=fake_instance.end,
                          flavor=fake_instance.flavor)

        self.database_adapter.get_all_entities_by_id_and_date.expect_called_once_with(
            fake_instance.entity_id, fake_instance.start, fake_instance.end
        )

    def test_list_entities(self):
        self.database_adapter.get_all_entities_by_project.return_value = ["volume2", "volume3", "instance1"]

        self.assertEqual(
            self.controller.list_entities("project_id", "start", "end"),
            ["volume2", "volume3", "instance1"]
        )

        self.database_adapter.get_all_entities_by_project.expect_called_once_with(
            "project_id", "start", "end"
        )

    def test_entity_exists(self):
        entity_id = "some_entity_id"
        self.database_adapter.count_entity_entries.return_value = 1

        self.assertEqual(True, self.controller.entity_exists(entity_id))

        self.database_adapter.count_entity_entries.expect_called_once_with(entity_id=entity_id)

    def test_entity_exists_not(self):
        entity_id = "some_entity_id"
        self.database_adapter.count_entity_entries.return_value = 0

        self.assertEqual(False, self.controller.entity_exists(entity_id))

        self.database_adapter.count_entity_entries.expect_called_once_with(entity_id=entity_id)

    def test_get_all_entities_by_id(self):
        entity_id = "some_entity_id"
        fake_entity = a(instance().with_id(entity_id))
        result = [fake_entity]
        self.database_adapter.count_entity_entries.return_value = 1
        self.database_adapter.get_all_entities_by_id.return_value = result

        self.assertEqual(result, self.controller.get_all_entities_by_id(entity_id))

        self.database_adapter.count_entity_entries.expect_called_once_with(entity_id=entity_id)
        self.database_adapter.get_all_entities_by_id.expect_called_once_with(entity_id=entity_id)

    def test_get_all_entities_by_id_when_entity_not_found(self):
        entity_id = "some_entity_id"
        self.database_adapter.count_entity_entries.return_value = 0

        self.assertRaises(exception.EntityNotFoundException,
                          self.controller.get_all_entities_by_id,
                          entity_id)

        self.database_adapter.count_entity_entries.expect_called_once_with(entity_id=entity_id)

    def test_instance_updated_wrong_attributes_raises_exception(self):
        fake_instance1 = a(instance())
        self.database_adapter.get_active_entity.return_value = fake_instance1

        self.assertRaises(exception.InvalidAttributeException,
                          self.controller.update_active_instance_entity,
                          instance_id=fake_instance1.entity_id,
                          wrong_attribute="this is wrong")

        self.database_adapter.get_active_entity.expect_called_once_with(fake_instance1.entity_id)

    def _expect_get_active_entity_and_update(self, fake_instance1, fake_instance2, **kwargs):
        self.database_adapter.get_active_entity.return_value = fake_instance1
        for key, value in kwargs.items():
            if key in ['start', 'end']:
                value = parse(value)

            setattr(fake_instance2, key, value)

        self.database_adapter.get_active_entity.expect_called_once_with(fake_instance1.entity_id)
        self.database_adapter.update_active_entity.expect_called_once_with(fake_instance2)
