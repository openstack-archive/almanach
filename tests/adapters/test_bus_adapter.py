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

import unittest
from datetime import datetime

import pytz
from flexmock import flexmock, flexmock_teardown

from almanach.common.exceptions.almanach_entity_not_found_exception import AlmanachEntityNotFoundException
from tests import messages
from almanach.adapters.bus_adapter import BusAdapter


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

    def test_rebuild(self):
        notification = messages.get_instance_rebuild_end_sample()
        self.controller \
            .should_receive("rebuild_instance") \
            .once()
        self.bus_adapter._instance_rebuilt(notification)

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

    def test_deleted_volume(self):
        notification = messages.get_volume_delete_end_sample()

        self.controller.should_receive('delete_volume').once()
        self.bus_adapter._volume_deleted(notification)

    def test_resize_volume(self):
        notification = messages.get_volume_update_end_sample()

        self.controller.should_receive('resize_volume').once()
        self.bus_adapter._volume_resized(notification)

    def test_deleted_instance(self):
        notification = messages.get_instance_delete_end_sample()

        self.controller.should_receive('delete_instance').once()
        self.bus_adapter._instance_deleted(notification)

    def test_instance_resized(self):
        notification = messages.get_instance_rebuild_end_sample()

        self.controller.should_receive('resize_instance').once()
        self.bus_adapter._instance_resized(notification)

    def test_updated_volume(self):
        notification = messages.get_volume_update_end_sample()

        self.controller.should_receive('resize_volume').once()
        self.bus_adapter._volume_resized(notification)

    def test_attach_volume_with_icehouse_payload(self):
        notification = messages.get_volume_attach_icehouse_end_sample(
            volume_id="my-volume-id",
            creation_timestamp=datetime(2014, 2, 14, 17, 18, 35, tzinfo=pytz.utc), attached_to="my-instance-id"
        )

        self.controller \
            .should_receive('attach_volume') \
            .with_args("my-volume-id", "2014-02-14T17:18:36.000000Z", ["my-instance-id"]) \
            .once()

        self.bus_adapter._volume_attached(notification)

    def test_attach_volume_with_kilo_payload(self):
        notification = messages.get_volume_attach_kilo_end_sample(
            volume_id="my-volume-id",
            timestamp=datetime(2014, 2, 14, 17, 18, 35, tzinfo=pytz.utc),
            attached_to=["I1"]
        )

        self.controller \
            .should_receive('attach_volume') \
            .with_args("my-volume-id", "2014-02-14T17:18:36.000000Z", ["I1"]) \
            .once()

        self.bus_adapter._volume_attached(notification)

    def test_attach_volume_with_kilo_payload_and_empty_attachments(self):
        notification = messages.get_volume_attach_kilo_end_sample(
            volume_id="my-volume-id",
            timestamp=datetime(2014, 2, 14, 17, 18, 35, tzinfo=pytz.utc),
            attached_to=[]
        )

        self.controller \
            .should_receive('attach_volume') \
            .with_args("my-volume-id", "2014-02-14T17:18:36.000000Z", []) \
            .once()

        self.bus_adapter._volume_attached(notification)

    def test_detached_volume(self):
        notification = messages.get_volume_detach_end_sample()

        (self.controller
         .should_receive('detach_volume')
         .once())

        self.bus_adapter._volume_detached(notification)

    def test_renamed_volume_with_volume_update_end(self):
        notification = messages.get_volume_update_end_sample()

        self.controller \
            .should_receive('rename_volume') \
            .once()

        self.bus_adapter._volume_renamed(notification)

    def test_renamed_volume_with_volume_exists(self):
        notification = messages.get_volume_exists_sample()

        self.controller.should_receive('rename_volume').once()
        self.bus_adapter._volume_renamed(notification)

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

    def test_get_attached_instances(self):
        self.assertEqual(["truc"], self.bus_adapter._get_attached_instances({"instance_uuid": "truc"}))
        self.assertEqual([], self.bus_adapter._get_attached_instances({"instance_uuid": None}))
        self.assertEqual([], self.bus_adapter._get_attached_instances({}))
        self.assertEqual(
            ["a", "b"],
            self.bus_adapter._get_attached_instances(
                {"volume_attachment": [{"instance_uuid": "a"}, {"instance_uuid": "b"}]}
            )
        )
        self.assertEqual(
            ["a"],
            self.bus_adapter._get_attached_instances({"volume_attachment": [{"instance_uuid": "a"}]})
        )
        self.assertEqual([], self.bus_adapter._get_attached_instances({"volume_attachment": []}))
