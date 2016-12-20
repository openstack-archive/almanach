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
from flexmock import flexmock
from hamcrest import assert_that
from hamcrest import calling
from hamcrest import raises
import pytz

from almanach.core.controllers import instance_controller
from almanach.core import exception
from almanach.core import model
from almanach.storage.drivers import base_driver
from almanach.tests.unit import base
from almanach.tests.unit.builder import a
from almanach.tests.unit.builder import instance


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

    def test_update_active_instance_entity_with_a_new_flavor(self):
        flavor = u"my flavor name"
        fake_instance1 = a(instance())
        fake_instance2 = copy(fake_instance1)
        self._expect_get_active_entity_and_update(fake_instance1, fake_instance2, flavor=flavor)

        self.controller.update_active_instance_entity(
            instance_id=fake_instance1.entity_id,
            flavor=flavor,
        )

    def test_update_active_instance_entity_with_a_new_name(self):
        name = u"my instance name"
        fake_instance1 = a(instance())
        fake_instance2 = copy(fake_instance1)
        self._expect_get_active_entity_and_update(fake_instance1, fake_instance2, name=name)

        self.controller.update_active_instance_entity(
            instance_id=fake_instance1.entity_id,
            name=name,
        )

    def test_update_active_instance_entity_with_a_new_os(self):
        os = {
            "os_type": u"linux",
            "version": u"7",
            "distro": u"centos"
        }
        fake_instance1 = a(instance())
        fake_instance2 = copy(fake_instance1)
        self._expect_get_active_entity_and_update(fake_instance1, fake_instance2, os=os)

        self.controller.update_active_instance_entity(
            instance_id=fake_instance1.entity_id,
            os=os,
        )

    def test_update_active_instance_entity_with_a_new_metadata(self):
        metadata = {
            "key": "value"
        }
        fake_instance1 = a(instance())
        fake_instance2 = copy(fake_instance1)
        self._expect_get_active_entity_and_update(fake_instance1, fake_instance2, metadata=metadata)

        self.controller.update_active_instance_entity(
            instance_id=fake_instance1.entity_id,
            metadata=metadata,
        )

    def test_update_active_instance_entity_with_a_new_start_date(self):
        fake_instance1 = a(instance())
        fake_instance2 = copy(fake_instance1)
        self._expect_get_active_entity_and_update(fake_instance1, fake_instance2, start="2015-10-21T16:25:00.000000Z")

        self.controller.update_active_instance_entity(
            instance_id=fake_instance1.entity_id,
            start_date="2015-10-21T16:25:00.000000Z",
        )

    def test_update_active_instance_entity_with_a_new_end_date(self):
        fake_instance1 = a(instance())
        fake_instance2 = copy(fake_instance1)
        self._expect_get_active_entity_and_update(fake_instance1, fake_instance2, end="2015-10-21T16:25:00.000000Z")

        self.controller.update_active_instance_entity(
            instance_id=fake_instance1.entity_id,
            end_date="2015-10-21T16:25:00.000000Z",
        )

    def test_instance_updated_wrong_attributes_raises_exception(self):
        fake_instance1 = a(instance())

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_instance1.entity_id)
         .and_return(fake_instance1)
         .never())

        assert_that(
                calling(self.controller.update_active_instance_entity).with_args(instance_id=fake_instance1.entity_id,
                                                                                 wrong_attribute="this is wrong"),
                raises(exception.InvalidAttributeException))

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
         .should_receive("list_entities")
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

    def _expect_get_active_entity_and_update(self, fake_instance1, fake_instance2, **kwargs):
        for key, value in kwargs.items():
            if key in ['start', 'end']:
                value = parse(value)

            setattr(fake_instance2, key, value)

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_instance1.entity_id)
         .and_return(fake_instance1)
         .once())
        (flexmock(self.database_adapter)
         .should_receive("update_active_entity")
         .with_args(fake_instance2)
         .once())
