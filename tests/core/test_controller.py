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

import sys
import logging
import unittest
from copy import copy
from datetime import datetime, timedelta

import pytz
from dateutil.parser import parse
from hamcrest import raises, calling, assert_that
from flexmock import flexmock, flexmock_teardown
from nose.tools import assert_raises

from almanach.common.exceptions.almanach_entity_not_found_exception import AlmanachEntityNotFoundException
from almanach.common.exceptions.multiple_entities_matching_query import MultipleEntitiesMatchingQuery
from tests.builder import a, instance, volume, volume_type
from almanach import config
from almanach.common.exceptions.date_format_exception import DateFormatException
from almanach.common.exceptions.validation_exception import InvalidAttributeException
from almanach.core.controller import Controller
from almanach.core.model import Instance, Volume

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class ControllerTest(unittest.TestCase):
    def setUp(self):
        self.database_adapter = flexmock()

        (flexmock(config)
         .should_receive("volume_existence_threshold")
         .and_return(10))
        (flexmock(config)
         .should_receive("device_metadata_whitelist")
         .and_return(["a_metadata.to_filter"]))

        self.controller = Controller(self.database_adapter)

    def tearDown(self):
        flexmock_teardown()

    def test_instance_created(self):
        fake_instance = a(instance().with_all_dates_in_string())

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_instance.entity_id)
         .and_raise(KeyError)
         .once())

        expected_instance = a(instance()
                              .with_id(fake_instance.entity_id)
                              .with_project_id(fake_instance.project_id)
                              .with_metadata({"a_metadata.to_filter": "include.this"}))

        (flexmock(self.database_adapter)
         .should_receive("insert_entity")
         .with_args(expected_instance)
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

    def test_update_entity_closed_entity_flavor(self):
        start = datetime(2016, 3, 1, 0, 0, 0, 0, pytz.utc)
        end = datetime(2016, 3, 3, 0, 0, 0, 0, pytz.utc)
        flavor = 'a_new_flavor'
        fake_instance1 = a(instance().with_start(2016, 3, 1, 0, 0, 0).with_end(2016, 3, 2, 0, 0, 0))

        (flexmock(self.database_adapter)
         .should_receive("list_entities_by_id")
         .with_args(fake_instance1.entity_id, start, end)
         .and_return([fake_instance1])
         .twice())

        (flexmock(self.database_adapter)
         .should_receive("update_closed_entity")
         .with_args(entity=fake_instance1, data={"flavor": flavor})
         .once())

        self.controller.update_inactive_entity(
            instance_id=fake_instance1.entity_id,
            start=start,
            end=end,
            flavor=flavor,
        )

    def test_update_one_close_entity_return_multiple_entities(self):
        fake_instances = [a(instance()), a(instance())]

        (flexmock(self.database_adapter)
         .should_receive("list_entities_by_id")
         .with_args(fake_instances[0].entity_id, fake_instances[0].start, fake_instances[0].end)
         .and_return(fake_instances)
         .once())

        assert_that(
            calling(self.controller.update_inactive_entity).with_args(instance_id=fake_instances[0].entity_id,
                                                                      start=fake_instances[0].start,
                                                                      end=fake_instances[0].end,
                                                                      flavor=fake_instances[0].flavor),
            raises(MultipleEntitiesMatchingQuery)
        )

    def test_update_one_close_entity_return_no_entity(self):
        fake_instances = a(instance())

        (flexmock(self.database_adapter)
         .should_receive("list_entities_by_id")
         .with_args(fake_instances.entity_id, fake_instances.start, fake_instances.end)
         .and_return([])
         .once())

        assert_that(
            calling(self.controller.update_inactive_entity).with_args(instance_id=fake_instances.entity_id,
                                                                      start=fake_instances.start,
                                                                      end=fake_instances.end,
                                                                      flavor=fake_instances.flavor),
            raises(AlmanachEntityNotFoundException)
        )

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
            raises(InvalidAttributeException))

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

        expected_instance = a(instance()
                              .with_id(fake_instance.entity_id)
                              .with_project_id(fake_instance.project_id)
                              .with_metadata({"a_metadata.to_filter": "include.this"}))

        (flexmock(self.database_adapter)
         .should_receive("insert_entity")
         .with_args(expected_instance)
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

        with self.assertRaises(AlmanachEntityNotFoundException):
            self.controller.delete_instance("id1", "2015-10-21T16:25:00.000000Z")

    def test_volume_deleted(self):
        fake_volume = a(volume())

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)
        date = date + timedelta(1)
        expected_date = pytz.utc.localize(date)

        (flexmock(self.database_adapter)
         .should_receive("count_entity_entries")
         .with_args(fake_volume.entity_id)
         .and_return(1))

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_volume.entity_id)
         .and_return(fake_volume))

        (flexmock(self.database_adapter)
         .should_receive("close_active_entity")
         .with_args(fake_volume.entity_id, expected_date)
         .once())

        self.controller.delete_volume(fake_volume.entity_id, date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

    def test_volume_deleted_within_volume_existance_threshold(self):
        fake_volume = a(volume())

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)
        date = date + timedelta(0, 5)

        (flexmock(self.database_adapter)
         .should_receive("count_entity_entries")
         .with_args(fake_volume.entity_id)
         .and_return(2))

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_volume.entity_id)
         .and_return(fake_volume))

        (flexmock(self.database_adapter)
         .should_receive("delete_active_entity")
         .with_args(fake_volume.entity_id)
         .once())

        self.controller.delete_volume(fake_volume.entity_id, date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

    def test_volume_deleted_within_volume_existance_threshold_but_with_only_one_entry(self):
        fake_volume = a(volume())

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)
        date = date + timedelta(0, 5)
        expected_date = pytz.utc.localize(date)

        (flexmock(self.database_adapter)
         .should_receive("count_entity_entries")
         .with_args(fake_volume.entity_id)
         .and_return(1))

        (flexmock(self.database_adapter)
         .should_receive("close_active_entity")
         .with_args(fake_volume.entity_id, expected_date)
         .once())

        self.controller.delete_volume(fake_volume.entity_id, date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

    def test_list_instances(self):
        (flexmock(self.database_adapter)
         .should_receive("list_entities")
         .with_args("project_id", "start", "end", Instance.TYPE)
         .and_return(["instance1", "instance2"])
         .once())

        self.assertEqual(self.controller.list_instances("project_id", "start", "end"), ["instance1", "instance2"])

    def test_list_volumes(self):
        (flexmock(self.database_adapter)
         .should_receive("list_entities")
         .with_args("project_id", "start", "end", Volume.TYPE)
         .and_return(["volume2", "volume3"]))

        self.assertEqual(self.controller.list_volumes("project_id", "start", "end"), ["volume2", "volume3"])

    def test_list_entities(self):
        (flexmock(self.database_adapter)
         .should_receive("list_entities")
         .with_args("project_id", "start", "end")
         .and_return(["volume2", "volume3", "instance1"]))

        self.assertEqual(self.controller.list_entities(
            "project_id", "start", "end"), ["volume2", "volume3", "instance1"])

    def test_create_volume(self):
        some_volume_type = a(volume_type().with_volume_type_name("some_volume_type_name"))
        (flexmock(self.database_adapter)
         .should_receive("get_volume_type")
         .with_args(some_volume_type.volume_type_id)
         .and_return(some_volume_type)
         .once())

        some_volume = a(volume()
                        .with_volume_type(some_volume_type.volume_type_name)
                        .with_all_dates_in_string())

        expected_volume = a(volume()
                            .with_volume_type(some_volume_type.volume_type_name)
                            .with_project_id(some_volume.project_id)
                            .with_id(some_volume.entity_id))

        (flexmock(self.database_adapter)
         .should_receive("insert_entity")
         .with_args(expected_volume)
         .once())
        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(some_volume.entity_id)
         .and_return(None)
         .once())

        self.controller.create_volume(some_volume.entity_id, some_volume.project_id, some_volume.start,
                                      some_volume_type.volume_type_id, some_volume.size, some_volume.name,
                                      some_volume.attached_to)

    def test_create_volume_raises_bad_date_format(self):
        some_volume = a(volume())

        assert_raises(
            DateFormatException,
            self.controller.create_volume,
            some_volume.entity_id,
            some_volume.project_id,
            'bad_date_format',
            some_volume.volume_type,
            some_volume.size,
            some_volume.name,
            some_volume.attached_to
        )

    def test_create_volume_insert_none_volume_type_as_type(self):
        some_volume_type = a(volume_type().with_volume_type_id(None).with_volume_type_name(None))
        (flexmock(self.database_adapter)
         .should_receive("get_volume_type")
         .never())

        some_volume = a(volume()
                        .with_volume_type(some_volume_type.volume_type_name)
                        .with_all_dates_in_string())

        expected_volume = a(volume()
                            .with_volume_type(some_volume_type.volume_type_name)
                            .with_project_id(some_volume.project_id)
                            .with_id(some_volume.entity_id))

        (flexmock(self.database_adapter)
         .should_receive("insert_entity")
         .with_args(expected_volume)
         .once())
        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(some_volume.entity_id)
         .and_return(None)
         .once())

        self.controller.create_volume(some_volume.entity_id, some_volume.project_id, some_volume.start,
                                      some_volume_type.volume_type_id, some_volume.size, some_volume.name,
                                      some_volume.attached_to)

    def test_create_volume_with_invalid_volume_type(self):
        some_volume_type = a(volume_type())
        (flexmock(self.database_adapter)
         .should_receive("get_volume_type")
         .with_args(some_volume_type.volume_type_id)
         .and_raise(KeyError)
         .once())

        some_volume = a(volume()
                        .with_volume_type(some_volume_type.volume_type_name)
                        .with_all_dates_in_string())

        (flexmock(self.database_adapter)
         .should_receive("insert_entity")
         .never())
        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(some_volume.entity_id)
         .and_return(None)
         .once())

        with self.assertRaises(KeyError):
            self.controller.create_volume(some_volume.entity_id, some_volume.project_id, some_volume.start,
                                          some_volume_type.volume_type_id, some_volume.size, some_volume.name,
                                          some_volume.attached_to)

    def test_create_volume_but_its_an_old_event(self):
        some_volume = a(volume().with_last_event(pytz.utc.localize(datetime(2015, 10, 21, 16, 29, 0))))
        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(some_volume.entity_id)
         .and_return(some_volume)
         .once())

        self.controller.create_volume(some_volume.entity_id, some_volume.project_id, '2015-10-21T16:25:00.000000Z',
                                      some_volume.volume_type, some_volume.size, some_volume.name,
                                      some_volume.attached_to)

    def test_volume_updated(self):
        fake_volume = a(volume())
        dates_str = "2015-10-21T16:25:00.000000Z"
        fake_volume.size = "new_size"
        fake_volume.start = parse(dates_str)
        fake_volume.end = None
        fake_volume.last_event = parse(dates_str)

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_volume.entity_id)
         .and_return(fake_volume)
         .once())
        (flexmock(self.database_adapter)
         .should_receive("close_active_entity")
         .with_args(fake_volume.entity_id, parse(dates_str))
         .once())

        (flexmock(self.database_adapter)
         .should_receive("insert_entity")
         .with_args(fake_volume)
         .once())

        self.controller.resize_volume(fake_volume.entity_id, "new_size", dates_str)

    def test_volume_attach_with_no_existing_attachment(self):
        fake_volume = a(volume()
                        .with_no_attachment())

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_volume.entity_id)
         .and_return(fake_volume)
         .once())

        (flexmock(self.database_adapter)
         .should_receive("update_active_entity")
         .with_args(fake_volume))

        self.controller.attach_volume(
            fake_volume.entity_id,
            date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            ["new_attached_to"]
        )
        self.assertEqual(fake_volume.attached_to, ["new_attached_to"])

    def test_volume_attach_with_existing_attachments(self):
        fake_volume = a(volume()
                        .with_attached_to(["existing_attached_to"]))

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_volume.entity_id)
         .and_return(fake_volume)
         .once())

        (flexmock(self.database_adapter)
         .should_receive("update_active_entity")
         .with_args(fake_volume))

        self.controller.attach_volume(
            fake_volume.entity_id,
            date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            ["existing_attached_to", "new_attached_to"]
        )
        self.assertEqual(fake_volume.attached_to, ["existing_attached_to", "new_attached_to"])

    def test_volume_attach_after_threshold(self):
        fake_volume = a(volume())

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)
        date = date + timedelta(0, 120)
        expected_date = pytz.utc.localize(date)

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_volume.entity_id)
         .and_return(fake_volume)
         .once())

        (flexmock(self.database_adapter)
         .should_receive("close_active_entity")
         .with_args(fake_volume.entity_id, expected_date)
         .once())

        new_volume = a(volume()
                       .build_from(fake_volume)
                       .with_datetime_start(expected_date)
                       .with_no_end()
                       .with_last_event(expected_date)
                       .with_attached_to(["new_attached_to"]))

        (flexmock(self.database_adapter)
         .should_receive("insert_entity")
         .with_args(new_volume)
         .once())

        self.controller.attach_volume(
            fake_volume.entity_id,
            date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            ["new_attached_to"]
        )

    def test_volume_detach_with_two_attachments(self):
        fake_volume = a(volume().with_attached_to(["I1", "I2"]))

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_volume.entity_id)
         .and_return(fake_volume)
         .once())

        (flexmock(self.database_adapter)
         .should_receive("update_active_entity")
         .with_args(fake_volume))

        self.controller.detach_volume(fake_volume.entity_id, date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), ["I2"])
        self.assertEqual(fake_volume.attached_to, ["I2"])

    def test_volume_detach_with_one_attachments(self):
        fake_volume = a(volume().with_attached_to(["I1"]))

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_volume.entity_id)
         .and_return(fake_volume)
         .once())

        (flexmock(self.database_adapter)
         .should_receive("update_active_entity")
         .with_args(fake_volume))

        self.controller.detach_volume(fake_volume.entity_id, date.strftime("%Y-%m-%dT%H:%M:%S.%f"), [])
        self.assertEqual(fake_volume.attached_to, [])

    def test_volume_detach_last_attachment_after_threshold(self):
        fake_volume = a(volume().with_attached_to(["I1"]))

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)
        date = date + timedelta(0, 120)
        expected_date = pytz.utc.localize(date)

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_volume.entity_id)
         .and_return(fake_volume)
         .once())

        (flexmock(self.database_adapter)
         .should_receive("close_active_entity")
         .with_args(fake_volume.entity_id, expected_date)
         .once())

        new_volume = a(volume()
                       .build_from(fake_volume)
                       .with_datetime_start(expected_date)
                       .with_no_end()
                       .with_last_event(expected_date)
                       .with_no_attachment())

        (flexmock(self.database_adapter)
         .should_receive("insert_entity")
         .with_args(new_volume)
         .once())

        self.controller.detach_volume(fake_volume.entity_id, date.strftime("%Y-%m-%dT%H:%M:%S.%f"), [])
        self.assertEqual(fake_volume.attached_to, [])

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

    def test_rename_volume(self):
        fake_volume = a(volume().with_display_name('old_volume_name'))

        volume_name = 'new_volume_name'

        (flexmock(self.database_adapter)
         .should_receive("get_active_entity")
         .with_args(fake_volume.entity_id)
         .and_return(fake_volume)
         .once())

        new_volume = a(volume().build_from(fake_volume).with_display_name(volume_name))

        (flexmock(self.database_adapter)
         .should_receive("update_active_entity")
         .with_args(new_volume)
         .once())

        self.controller.rename_volume(fake_volume.entity_id, volume_name)

    def test_volume_type_created(self):
        fake_volume_type = a(volume_type())

        (flexmock(self.database_adapter)
         .should_receive("insert_volume_type")
         .with_args(fake_volume_type)
         .once())

        self.controller.create_volume_type(fake_volume_type.volume_type_id, fake_volume_type.volume_type_name)

    def test_get_volume_type(self):
        some_volume = a(volume_type())
        (flexmock(self.database_adapter)
         .should_receive("get_volume_type")
         .and_return(some_volume)
         .once())

        returned_volume_type = self.controller.get_volume_type(some_volume.volume_type_id)

        self.assertEqual(some_volume, returned_volume_type)

    def test_delete_volume_type(self):
        some_volume = a(volume_type())
        (flexmock(self.database_adapter)
         .should_receive("delete_volume_type")
         .once())

        self.controller.delete_volume_type(some_volume.volume_type_id)

    def test_list_volume_types(self):
        some_volumes = [a(volume_type()), a(volume_type())]
        (flexmock(self.database_adapter)
         .should_receive("list_volume_types")
         .and_return(some_volumes)
         .once())

        self.assertEqual(len(self.controller.list_volume_types()), 2)

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
