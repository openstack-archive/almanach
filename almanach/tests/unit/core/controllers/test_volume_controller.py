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
from datetime import timedelta
from dateutil.parser import parse
from flexmock import flexmock
import pytz

from almanach.core.controllers import volume_controller
from almanach.core import exception
from almanach.core import model
from almanach.storage.drivers import base_driver
from almanach.tests.unit import base
from almanach.tests.unit.builder import a
from almanach.tests.unit.builder import volume
from almanach.tests.unit.builder import volume_type


class VolumeControllerTest(base.BaseTestCase):

    def setUp(self):
        super(VolumeControllerTest, self).setUp()
        self.database_adapter = flexmock(base_driver.BaseDriver)
        self.controller = volume_controller.VolumeController(self.config, self.database_adapter)

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

    def test_list_volumes(self):
        (flexmock(self.database_adapter)
         .should_receive("list_entities")
         .with_args("project_id", "start", "end", model.Volume.TYPE)
         .and_return(["volume2", "volume3"]))

        self.assertEqual(self.controller.list_volumes("project_id", "start", "end"), ["volume2", "volume3"])

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

        self.assertRaises(
            exception.DateFormatException,
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

        self.assertRaises(KeyError, self.controller.create_volume,
                          some_volume.entity_id, some_volume.project_id, some_volume.start,
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
