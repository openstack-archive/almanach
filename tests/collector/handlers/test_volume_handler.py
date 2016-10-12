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
from flexmock import flexmock
import pytz

from almanach.collector.handlers import volume_handler
from integration_tests.builders import messages
from tests import base


class VolumeHandlerTest(base.BaseTestCase):

    def setUp(self):
        super(VolumeHandlerTest, self).setUp()

        self.controller = flexmock()
        self.retry = flexmock()
        self.volume_handler = volume_handler.VolumeHandler(self.controller)

    def test_deleted_volume(self):
        notification = messages.get_volume_delete_end_sample()

        self.controller.should_receive('delete_volume').once()
        self.volume_handler.on_volume_deleted(notification)

    def test_resize_volume(self):
        notification = messages.get_volume_update_end_sample()

        self.controller.should_receive('resize_volume').once()
        self.volume_handler.on_volume_resized(notification)

    def test_updated_volume(self):
        notification = messages.get_volume_update_end_sample()

        self.controller.should_receive('resize_volume').once()
        self.volume_handler.on_volume_resized(notification)

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

        self.volume_handler.on_volume_attached(notification)

    def test_detached_volume(self):
        notification = messages.get_volume_detach_end_sample()

        (self.controller
         .should_receive('detach_volume')
         .once())

        self.volume_handler.on_volume_detached(notification)

    def test_renamed_volume_with_volume_update_end(self):
        notification = messages.get_volume_update_end_sample()

        self.controller \
            .should_receive('rename_volume') \
            .once()

        self.volume_handler.on_volume_renamed(notification)

    def test_renamed_volume_with_volume_exists(self):
        notification = messages.get_volume_exists_sample()

        self.controller.should_receive('rename_volume').once()
        self.volume_handler.on_volume_renamed(notification)

    def test_attach_volume_with_icehouse_payload(self):
        notification = messages.get_volume_attach_icehouse_end_sample(
            volume_id="my-volume-id",
            creation_timestamp=datetime(2014, 2, 14, 17, 18, 35, tzinfo=pytz.utc), attached_to="my-instance-id"
        )

        self.controller \
            .should_receive('attach_volume') \
            .with_args("my-volume-id", "2014-02-14T17:18:36.000000Z", ["my-instance-id"]) \
            .once()

        self.volume_handler.on_volume_attached(notification)

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

        self.volume_handler.on_volume_attached(notification)

    def test_get_attached_instances(self):
        self.assertEqual(["truc"], self.volume_handler._get_attached_instances({"instance_uuid": "truc"}))
        self.assertEqual([], self.volume_handler._get_attached_instances({"instance_uuid": None}))
        self.assertEqual([], self.volume_handler._get_attached_instances({}))
        self.assertEqual(
            ["a", "b"],
            self.volume_handler._get_attached_instances(
                {"volume_attachment": [{"instance_uuid": "a"}, {"instance_uuid": "b"}]}
            )
        )
        self.assertEqual(
            ["a"],
            self.volume_handler._get_attached_instances({"volume_attachment": [{"instance_uuid": "a"}]})
        )
        self.assertEqual([], self.volume_handler._get_attached_instances({"volume_attachment": []}))
