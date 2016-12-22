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
from flexmock import flexmock
import pytz

from almanach.core.controllers import instance_controller
from almanach.core import exception
from almanach.core import model
from almanach.storage.drivers import base_driver

from almanach.tests.unit import base
from almanach.tests.unit.builders.entity import a
from almanach.tests.unit.builders.entity import instance


class InstanceControllerTest(base.BaseTestCase):

    def setUp(self):
        super(InstanceControllerTest, self).setUp()
        self.database_adapter = flexmock(base_driver.BaseDriver)
        self.controller = instance_controller.InstanceController(self.config, self.database_adapter)

    def test_instance_created(self):
        fake_instance = a(instance().with_all_dates_in_string())

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_instance.entity_id)
         .and_raise(KeyError)
         .once())

        (flexmock(self.database_adapter)
         .should_receive("insert_entity")
         .once())

        self.controller.create_instance(fake_instance.entity_id, fake_instance.project_id, fake_instance.start,
                                        fake_instance.flavor, fake_instance.os.os_type, fake_instance.os.distro,
                                        fake_instance.os.version, fake_instance.name, fake_instance.metadata)

    def test_resize_instance(self):
        fake_instance = a(instance())

        dates_str = "2015-10-21T16:25:00.000000Z"
        fake_instance.start = parse(dates_str)
        fake_instance.end = None
        fake_instance.last_event = parse(dates_str)

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_instance.entity_id)
         .and_return(fake_instance)
         .once())
        (flexmock(self.database_adapter)
         .should_receive("close_active_entity")
         .with_args(fake_instance.entity_id, parse(dates_str))
         .once())

        (flexmock(self.database_adapter)
         .should_receive("insert_entity")
         .with_args(fake_instance)
         .once())

        self.controller.resize_instance(fake_instance.entity_id, "newly_flavor", dates_str)

    def test_instance_created_but_its_an_old_event(self):
        fake_instance = a(instance()
                          .with_last_event(pytz.utc.localize(datetime(2015, 10, 21, 16, 29, 0))))

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_instance.entity_id)
         .and_return(fake_instance)
         .once())

        self.controller.create_instance(fake_instance.entity_id, fake_instance.project_id,
                                        '2015-10-21T16:25:00.000000Z',
                                        fake_instance.flavor, fake_instance.os.os_type, fake_instance.os.distro,
                                        fake_instance.os.version, fake_instance.name, fake_instance.metadata)

    def test_instance_created_but_find_garbage(self):
        fake_instance = a(instance().with_all_dates_in_string())

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_instance.entity_id)
         .and_raise(NotImplementedError)  # The db adapter found garbage in the database, we will ignore this entry
         .once())

        (flexmock(self.database_adapter)
         .should_receive("insert_entity")
         .once())

        self.controller.create_instance(fake_instance.entity_id, fake_instance.project_id, fake_instance.start,
                                        fake_instance.flavor, fake_instance.os.os_type, fake_instance.os.distro,
                                        fake_instance.os.version, fake_instance.name, fake_instance.metadata)

    def test_instance_deleted(self):
        (flexmock(self.database_adapter)
         .should_receive("has_active_entity")
         .with_args("id1")
         .and_return(True)
         .once())

        (flexmock(self.database_adapter)
         .should_receive("close_active_entity")
         .with_args("id1", parse("2015-10-21T16:25:00.000000Z"))
         .once())

        self.controller.delete_instance("id1", "2015-10-21T16:25:00.000000Z")

    def test_instance_deleted_when_entity_not_found(self):
        (flexmock(self.database_adapter)
         .should_receive("has_active_entity")
         .with_args("id1")
         .and_return(False)
         .once())

        self.assertRaises(exception.AlmanachEntityNotFoundException,
                          self.controller.delete_instance,
                          "id1", "2015-10-21T16:25:00.000000Z")

    def test_list_instances(self):
        (flexmock(self.database_adapter)
         .should_receive("get_all_entities_by_project")
         .with_args("project_id", "start", "end", model.Instance.TYPE)
         .and_return(["instance1", "instance2"])
         .once())

        self.assertEqual(self.controller.list_instances("project_id", "start", "end"), ["instance1", "instance2"])

    def test_instance_rebuilded(self):
        i = a(instance())

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .and_return(i)
         .twice())
        (flexmock(self.database_adapter)
         .should_receive("close_active_entity")
         .once())
        (flexmock(self.database_adapter)
         .should_receive("insert_entity")
         .once())

        self.controller.rebuild_instance(
            "an_instance_id",
            "some_distro",
            "some_version",
            "some_type",
            "2015-10-21T16:25:00.000000Z"
        )
        self.controller.rebuild_instance(
            "an_instance_id",
            i.os.distro,
            i.os.version,
            i.os.os_type,
            "2015-10-21T16:25:00.000000Z"
        )
