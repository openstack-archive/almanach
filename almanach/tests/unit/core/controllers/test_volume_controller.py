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
import mock
import pytz

from almanach.core.controllers import volume_controller
from almanach.core import exception
from almanach.core import model
from almanach.storage.drivers import base_driver

from almanach.tests.unit import base
from almanach.tests.unit.builders.entity import a
from almanach.tests.unit.builders.entity import volume
from almanach.tests.unit.builders.entity import volume_type


class TestVolumeController(base.BaseTestCase):

    def setUp(self):
        super(TestVolumeController, self).setUp()
        self.database_adapter = mock.Mock(spec=base_driver.BaseDriver)
        self.controller = volume_controller.VolumeController(self.config, self.database_adapter)

    def test_volume_closed(self):
        fake_volume = a(volume())
        self.database_adapter.count_entity_entries.return_value = 2
        self.database_adapter.get_active_entity.return_value = fake_volume

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)
        date = date + timedelta(1)
        expected_date = pytz.utc.localize(date)

        self.controller.delete_volume(fake_volume.entity_id, date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

        self.database_adapter.count_entity_entries.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.get_active_entity.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.close_active_entity.assert_called_once_with(fake_volume.entity_id, expected_date)

    def test_volume_deleted_within_volume_existance_threshold(self):
        fake_volume = a(volume())
        self.database_adapter.count_entity_entries.return_value = 2
        self.database_adapter.get_active_entity.return_value = fake_volume

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)
        date = date + timedelta(0, 5)

        self.controller.delete_volume(fake_volume.entity_id, date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

        self.database_adapter.count_entity_entries.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.get_active_entity.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.delete_active_entity.assert_called_once_with(fake_volume.entity_id)

    def test_volume_deleted_within_volume_existance_threshold_but_with_only_one_entry(self):
        fake_volume = a(volume())
        self.database_adapter.count_entity_entries.return_value = 1

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)
        date = date + timedelta(0, 5)
        expected_date = pytz.utc.localize(date)

        self.controller.delete_volume(fake_volume.entity_id, date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

        self.database_adapter.count_entity_entries.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.close_active_entity.assert_called_once_with(fake_volume.entity_id, expected_date)

    def test_list_volumes(self):
        self.database_adapter.get_all_entities_by_project.return_value = ["volume2", "volume3"]

        self.assertEqual(self.controller.list_volumes("project_id", "start", "end"), ["volume2", "volume3"])

        self.database_adapter.get_all_entities_by_project.assert_called_once_with(
            "project_id", "start", "end", model.Volume.TYPE
        )

    def test_create_volume(self):
        some_volume_type = a(volume_type().with_volume_type_name("some_volume_type_name"))
        self.database_adapter.get_volume_type.return_value = some_volume_type
        self.database_adapter.get_active_entity.return_value = None

        some_volume = a(volume()
                        .with_volume_type(some_volume_type.volume_type_name)
                        .with_all_dates_in_string())

        expected_volume = a(volume()
                            .with_volume_type(some_volume_type.volume_type_name)
                            .with_project_id(some_volume.project_id)
                            .with_id(some_volume.entity_id))

        self.controller.create_volume(some_volume.entity_id, some_volume.project_id, some_volume.start,
                                      some_volume_type.volume_type_id, some_volume.size, some_volume.name,
                                      some_volume.attached_to)

        self.database_adapter.get_volume_type.assert_called_once_with(some_volume_type.volume_type_id)
        self.database_adapter.insert_entity.assert_called_once_with(expected_volume)
        self.database_adapter.get_active_entity.assert_called_once_with(some_volume.entity_id)

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
        self.database_adapter.get_active_entity.return_value = None

        some_volume = a(volume()
                        .with_volume_type(some_volume_type.volume_type_name)
                        .with_all_dates_in_string())

        expected_volume = a(volume()
                            .with_volume_type(some_volume_type.volume_type_name)
                            .with_project_id(some_volume.project_id)
                            .with_id(some_volume.entity_id))

        self.controller.create_volume(some_volume.entity_id, some_volume.project_id, some_volume.start,
                                      some_volume_type.volume_type_id, some_volume.size, some_volume.name,
                                      some_volume.attached_to)

        self.database_adapter.get_volume_type.assert_not_called()
        self.database_adapter.insert_entity.assert_called_once_with(expected_volume)
        self.database_adapter.get_active_entity.assert_called_once_with(some_volume.entity_id)

    def test_create_volume_with_invalid_volume_type(self):
        some_volume_type = a(volume_type())
        self.database_adapter.get_volume_type.side_effect = exception.VolumeTypeNotFoundException
        self.database_adapter.get_active_entity.return_value = None

        some_volume = a(volume()
                        .with_volume_type(some_volume_type.volume_type_name)
                        .with_all_dates_in_string())

        self.assertRaises(exception.VolumeTypeNotFoundException, self.controller.create_volume,
                          some_volume.entity_id, some_volume.project_id, some_volume.start,
                          some_volume_type.volume_type_id, some_volume.size, some_volume.name,
                          some_volume.attached_to)

        self.database_adapter.get_volume_type.assert_called_once_with(some_volume_type.volume_type_id)
        self.database_adapter.insert_entity.assert_not_called()
        self.database_adapter.get_active_entity.assert_called_once_with(some_volume.entity_id)

    def test_create_volume_but_its_an_old_event(self):
        some_volume = a(volume().with_last_event(pytz.utc.localize(datetime(2015, 10, 21, 16, 29, 0))))
        self.database_adapter.get_active_entity.return_value = some_volume

        self.controller.create_volume(some_volume.entity_id, some_volume.project_id, '2015-10-21T16:25:00.000000Z',
                                      some_volume.volume_type, some_volume.size, some_volume.name,
                                      some_volume.attached_to)

        self.database_adapter.get_active_entity.assert_called_once_with(some_volume.entity_id)

    def test_volume_updated(self):
        fake_volume = a(volume())
        dates_str = "2015-10-21T16:25:00.000000Z"
        fake_volume.size = "new_size"
        fake_volume.start = parse(dates_str)
        fake_volume.end = None
        fake_volume.last_event = parse(dates_str)
        self.database_adapter.get_active_entity.return_value = fake_volume

        self.controller.resize_volume(fake_volume.entity_id, "new_size", dates_str)

        self.database_adapter.get_active_entity.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.close_active_entity.assert_called_once_with(fake_volume.entity_id, parse(dates_str))
        self.database_adapter.insert_entity.assert_called_once_with(fake_volume)

    def test_volume_attach_with_no_existing_attachment(self):
        fake_volume = a(volume()
                        .with_no_attachment())
        self.database_adapter.get_active_entity.return_value = fake_volume

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)

        self.controller.attach_volume(
            fake_volume.entity_id,
            date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            ["new_attached_to"]
        )

        self.assertEqual(fake_volume.attached_to, ["new_attached_to"])
        self.database_adapter.get_active_entity.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.update_active_entity.assert_called_once_with(fake_volume)

    def test_volume_attach_with_existing_attachments(self):
        fake_volume = a(volume()
                        .with_attached_to(["existing_attached_to"]))
        self.database_adapter.get_active_entity.return_value = fake_volume

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)

        self.controller.attach_volume(
            fake_volume.entity_id,
            date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            ["existing_attached_to", "new_attached_to"]
        )

        self.assertEqual(fake_volume.attached_to, ["existing_attached_to", "new_attached_to"])
        self.database_adapter.get_active_entity.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.update_active_entity.assert_called_once_with(fake_volume)

    def test_volume_attach_after_threshold(self):
        fake_volume = a(volume())
        self.database_adapter.get_active_entity.return_value = fake_volume

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)
        date = date + timedelta(0, 120)
        expected_date = pytz.utc.localize(date)

        new_volume = a(volume()
                       .build_from(fake_volume)
                       .with_datetime_start(expected_date)
                       .with_no_end()
                       .with_last_event(expected_date)
                       .with_attached_to(["new_attached_to"]))

        self.controller.attach_volume(
            fake_volume.entity_id,
            date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            ["new_attached_to"]
        )

        self.database_adapter.get_active_entity.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.close_active_entity.assert_called_once_with(fake_volume.entity_id, expected_date)
        self.database_adapter.insert_entity.assert_called_once_with(new_volume)

    def test_volume_detach_with_two_attachments(self):
        fake_volume = a(volume().with_attached_to(["I1", "I2"]))
        self.database_adapter.get_active_entity.return_value = fake_volume

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)

        self.controller.detach_volume(fake_volume.entity_id, date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), ["I2"])

        self.assertEqual(fake_volume.attached_to, ["I2"])
        self.database_adapter.get_active_entity.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.update_active_entity.assert_called_once_with(fake_volume)

    def test_volume_detach_with_one_attachments(self):
        fake_volume = a(volume().with_attached_to(["I1"]))
        self.database_adapter.get_active_entity.return_value = fake_volume

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)

        self.controller.detach_volume(fake_volume.entity_id, date.strftime("%Y-%m-%dT%H:%M:%S.%f"), [])

        self.assertEqual(fake_volume.attached_to, [])
        self.database_adapter.get_active_entity.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.update_active_entity.assert_called_once_with(fake_volume)

    def test_volume_detach_last_attachment_after_threshold(self):
        fake_volume = a(volume().with_attached_to(["I1"]))
        self.database_adapter.get_active_entity.return_value = fake_volume

        date = datetime(fake_volume.start.year, fake_volume.start.month, fake_volume.start.day, fake_volume.start.hour,
                        fake_volume.start.minute, fake_volume.start.second, fake_volume.start.microsecond)
        date = date + timedelta(0, 120)
        expected_date = pytz.utc.localize(date)

        new_volume = a(volume()
                       .build_from(fake_volume)
                       .with_datetime_start(expected_date)
                       .with_no_end()
                       .with_last_event(expected_date)
                       .with_no_attachment())

        self.controller.detach_volume(fake_volume.entity_id, date.strftime("%Y-%m-%dT%H:%M:%S.%f"), [])

        self.assertEqual(fake_volume.attached_to, [])
        self.database_adapter.get_active_entity.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.close_active_entity.assert_called_once_with(fake_volume.entity_id, expected_date)
        self.database_adapter.insert_entity.assert_called_once_with(new_volume)

    def test_rename_volume(self):
        fake_volume = a(volume().with_display_name('old_volume_name'))
        volume_name = 'new_volume_name'
        self.database_adapter.get_active_entity.return_value = fake_volume

        new_volume = a(volume().build_from(fake_volume).with_display_name(volume_name))

        self.controller.rename_volume(fake_volume.entity_id, volume_name)

        self.database_adapter.get_active_entity.assert_called_once_with(fake_volume.entity_id)
        self.database_adapter.update_active_entity.assert_called_once_with(new_volume)
