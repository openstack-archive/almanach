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

from datetime import datetime
from dateutil.parser import parse
import mock
import pytz

from almanach.core.controllers import instance_controller
from almanach.core import exception
from almanach.core import model
from almanach.storage.drivers import base_driver

from almanach.tests.unit import base
from almanach.tests.unit.builders.entity import a
from almanach.tests.unit.builders.entity import instance


class TestInstanceController(base.BaseTestCase):

    def setUp(self):
        super(TestInstanceController, self).setUp()
        self.config.entities.instance_image_meta = ['distro', 'version', 'os_type']
        self.database_adapter = mock.Mock(spec=base_driver.BaseDriver)
        self.controller = instance_controller.InstanceController(self.config, self.database_adapter)

    def test_instance_created(self):
        fake_instance = a(instance().with_all_dates_in_string())
        self.database_adapter.get_active_entity.side_effect = exception.EntityNotFoundException

        self.controller.create_instance(fake_instance.entity_id,
                                        fake_instance.project_id,
                                        fake_instance.start,
                                        fake_instance.flavor,
                                        fake_instance.name,
                                        fake_instance.image_meta,
                                        fake_instance.metadata)

        self.database_adapter.get_active_entity.assert_called_once_with(fake_instance.entity_id)
        self.database_adapter.insert_entity.assert_called_once()

    def test_resize_instance(self):
        fake_instance = a(instance())
        self.database_adapter.get_active_entity.return_value = fake_instance

        dates_str = "2015-10-21T16:25:00.000000Z"
        fake_instance.start = parse(dates_str)
        fake_instance.end = None
        fake_instance.last_event = parse(dates_str)

        self.controller.resize_instance(fake_instance.entity_id, "newly_flavor", dates_str)

        self.database_adapter.get_active_entity.assert_called_once_with(fake_instance.entity_id)
        self.database_adapter.close_active_entity.assert_called_once_with(fake_instance.entity_id, parse(dates_str))
        self.database_adapter.insert_entity.assert_called_once_with(fake_instance)

    def test_instance_created_but_its_an_old_event(self):
        fake_instance = a(instance()
                          .with_last_event(pytz.utc.localize(datetime(2015, 10, 21, 16, 29, 0))))
        self.database_adapter.get_active_entity.return_value = fake_instance

        self.controller.create_instance(fake_instance.entity_id, fake_instance.project_id,
                                        '2015-10-21T16:25:00.000000Z',
                                        fake_instance.flavor, fake_instance.image_meta, fake_instance.metadata)

        self.database_adapter.get_active_entity.assert_called_once_with(fake_instance.entity_id)

    def test_instance_created_but_find_garbage(self):
        fake_instance = a(instance().with_all_dates_in_string())
        self.database_adapter.get_active_entity.side_effect = exception.EntityTypeNotSupportedException

        self.controller.create_instance(fake_instance.entity_id, fake_instance.project_id, fake_instance.start,
                                        fake_instance.flavor, fake_instance.image_meta, fake_instance.metadata)

        self.database_adapter.get_active_entity.assert_called_once_with(fake_instance.entity_id)
        self.database_adapter.insert_entity.assert_called_once()

    def test_instance_deleted(self):
        self.database_adapter.has_active_entity.return_value = True

        self.controller.delete_instance("id1", "2015-10-21T16:25:00.000000Z")

        self.database_adapter.has_active_entity.assert_called_once_with("id1")
        self.database_adapter.close_active_entity.assert_called_once_with("id1", parse("2015-10-21T16:25:00.000000Z"))

    def test_instance_deleted_when_entity_not_found(self):
        self.database_adapter.has_active_entity.return_value = False

        self.assertRaises(exception.EntityNotFoundException,
                          self.controller.delete_instance,
                          "id1", "2015-10-21T16:25:00.000000Z")

        self.database_adapter.has_active_entity.assert_called_once_with("id1")

    def test_list_instances(self):
        self.database_adapter.get_all_entities_by_project.return_value = ["instance1", "instance2"]

        self.assertEqual(self.controller.list_instances("project_id", "start", "end"), ["instance1", "instance2"])

        self.database_adapter.get_all_entities_by_project.assert_called_once_with(
            "project_id", "start", "end", model.Instance.TYPE
        )

    def test_instance_rebuilded(self):
        i = a(instance())
        self.database_adapter.get_active_entity.side_effect = [i, i]
        calls = [mock.call("an_instance_id"), mock.call("an_instance_id")]

        self.controller.rebuild_instance(
            "an_instance_id",
            "2015-10-21T16:25:00.000000Z",
            dict(distro="some_distro", version="some_version", os_type="some_type")
        )
        self.controller.rebuild_instance(
            "an_instance_id",
            "2015-10-21T16:25:00.000000Z",
            dict(distro=i.image_meta['distro'], version=i.image_meta['version'], os_type=i.image_meta['os_type'])
        )

        self.database_adapter.get_active_entity.assert_has_calls(calls)
        self.database_adapter.close_active_entity.assert_called_once()
        self.database_adapter.insert_entity.assert_called_once()
