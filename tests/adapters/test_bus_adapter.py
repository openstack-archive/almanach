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

import pytz
import unittest
from datetime import datetime
from flexmock import flexmock, flexmock_teardown

from almanach.adapters.bus_adapter import BusAdapter
from almanach.common.exceptions.almanach_entity_not_found_exception import AlmanachEntityNotFoundException
from integration_tests.builders import messages


class BusAdapterTest(unittest.TestCase):

    def setUp(self):
        self.controller = flexmock()
        self.retry = flexmock()
        self.bus_adapter = BusAdapter(self.controller, None, retry_adapter=self.retry)

    def tearDown(self):
        flexmock_teardown()

    def test_on_message(self):
        instance_id = "e7d44dea-21c1-452c-b50c-cbab0d07d7d3"
        tenant_id = "0be9215b503b43279ae585d50a33aed8"
        instance_type = "myflavor"
        timestamp = datetime(2014, 02, 14, 16, 30, 10, tzinfo=pytz.utc)
        hostname = "some hostname"
        metadata = {"a_metadata.to_filter": "filtered_value", }

        notification = messages.get_instance_create_end_sample(instance_id=instance_id, tenant_id=tenant_id,
                                                               flavor_name=instance_type, creation_timestamp=timestamp,
                                                               name=hostname, metadata=metadata)
        os_type = notification.get("payload").get("image_meta").get("os_type")
        distro = notification.get("payload").get("image_meta").get("distro")
        version = notification.get("payload").get("image_meta").get("version")
        metadata = notification.get("payload").get("metadata")

        self.controller \
            .should_receive("create_instance") \
            .with_args(
                instance_id,
                tenant_id,
                timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                instance_type,
                os_type,
                distro,
                version,
                hostname,
                metadata
            ) \
            .once()

        message = flexmock()
        message.should_receive("ack")

        self.bus_adapter.on_message(notification, message)

    def test_on_message_with_empty_metadata(self):
        instance_id = "e7d44dea-21c1-452c-b50c-cbab0d07d7d3"
        tenant_id = "0be9215b503b43279ae585d50a33aed8"
        instance_type = "myflavor"
        timestamp = datetime(2014, 02, 14, 16, 30, 10, tzinfo=pytz.utc)
        hostname = "some hostname"

        notification = messages.get_instance_create_end_sample(instance_id=instance_id, tenant_id=tenant_id,
                                                               flavor_name=instance_type, creation_timestamp=timestamp,
                                                               name=hostname, metadata={})
        os_type = notification.get("payload").get("image_meta").get("os_type")
        distro = notification.get("payload").get("image_meta").get("distro")
        version = notification.get("payload").get("image_meta").get("version")
        metadata = notification.get("payload").get("metadata")

        self.controller \
            .should_receive("create_instance") \
            .with_args(
                instance_id, tenant_id, timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), instance_type, os_type,
                distro, version, hostname, metadata
            ) \
            .once()

        message = flexmock()
        (flexmock(message)
         .should_receive("ack"))

        self.bus_adapter.on_message(notification, message)

    def test_on_message_with_delete_instance(self):
        notification = messages.get_instance_delete_end_sample()

        self.controller \
            .should_receive("delete_instance") \
            .with_args(
                notification['payload']['instance_id'],
                notification['payload']['terminated_at']
            ) \
            .once()

        message = flexmock()
        (flexmock(message)
         .should_receive("ack"))

        self.bus_adapter.on_message(notification, message)

    def test_on_message_with_rebuild_instance(self):
        notification = messages.get_instance_rebuild_end_sample()

        self.controller \
            .should_receive("rebuild_instance") \
            .with_args(
                notification['payload']['instance_id'],
                notification['payload']['image_meta']['distro'],
                notification['payload']['image_meta']['version'],
                notification['payload']['image_meta']['os_type'],
                notification['timestamp'],
            ) \
            .once()

        message = flexmock()
        (flexmock(message)
         .should_receive("ack"))

        self.bus_adapter.on_message(notification, message)

    def test_on_message_with_resize_instance(self):
        notification = messages.get_instance_resized_end_sample()

        self.controller \
            .should_receive("resize_instance") \
            .with_args(
                notification['payload']['instance_id'],
                notification['payload']['instance_type'],
                notification['timestamp'],
            )\
            .once()

        message = flexmock()
        (flexmock(message)
         .should_receive("ack"))

        self.bus_adapter.on_message(notification, message)

    def test_on_message_with_resize_volume(self):
        notification = messages.get_volume_update_end_sample()

        self.controller \
            .should_receive("resize_volume") \
            .with_args(
                notification['payload']['volume_id'],
                notification['payload']['size'],
                notification['timestamp'],
            ) \
            .once()

        message = flexmock()
        (flexmock(message)
         .should_receive("ack"))

        self.bus_adapter.on_message(notification, message)

    def test_on_message_with_volume(self):
        volume_id = "vol_id"
        tenant_id = "tenant_id"
        timestamp_datetime = datetime(2014, 02, 14, 16, 30, 10, tzinfo=pytz.utc)
        volume_type = "SF400"
        volume_size = 100000
        some_volume = "volume_name"

        notification = messages.get_volume_create_end_sample(volume_id=volume_id, tenant_id=tenant_id,
                                                             volume_type=volume_type, volume_size=volume_size,
                                                             creation_timestamp=timestamp_datetime, name=some_volume)
        self.controller \
            .should_receive("create_volume") \
            .with_args(
                volume_id, tenant_id, timestamp_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), volume_type,
                volume_size, some_volume
            ) \
            .once()

        message = flexmock()
        (flexmock(message)
         .should_receive("ack"))

        self.bus_adapter.on_message(notification, message)

    def test_on_message_with_volume_type(self):
        volume_type_id = "an_id"
        volume_type_name = "a_name"

        notification = messages.get_volume_type_create_sample(volume_type_id=volume_type_id,
                                                              volume_type_name=volume_type_name)

        self.controller \
            .should_receive("create_volume_type") \
            .with_args(volume_type_id, volume_type_name) \
            .once()

        message = flexmock()
        (flexmock(message)
         .should_receive("ack"))

        self.bus_adapter.on_message(notification, message)

    def test_on_message_with_delete_volume(self):
        notification = messages.get_volume_delete_end_sample()

        self.controller \
            .should_receive("delete_volume") \
            .with_args(
                notification['payload']['volume_id'],
                notification['timestamp'],
            ) \
            .once()

        message = flexmock()
        (flexmock(message)
         .should_receive("ack"))

        self.bus_adapter.on_message(notification, message)

    def test_failing_notification_get_retry(self):
        notification = messages.get_instance_rebuild_end_sample()
        message = flexmock()

        (flexmock(message).should_receive("ack"))
        self.controller.should_receive('instance_rebuilded').and_raise(Exception("Foobar"))
        self.retry.should_receive('publish_to_dead_letter').with_args(message).once()

        self.bus_adapter.on_message(notification, message)

    def test_that_entity_not_found_exceptions_goes_to_retry_queue(self):
        notification = messages.get_instance_delete_end_sample(instance_id="My instance id")
        message = flexmock()

        (flexmock(message).should_receive("ack"))
        self.controller.should_receive('delete_instance').and_raise(AlmanachEntityNotFoundException("Entity not found"))
        self.retry.should_receive('publish_to_dead_letter').with_args(message).once()

        self.bus_adapter.on_message(notification, message)
