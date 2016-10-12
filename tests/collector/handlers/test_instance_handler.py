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

from flexmock import flexmock

from almanach.collector.handlers import instance_handler
from integration_tests.builders import messages
from tests import base


class InstanceHandlerTest(base.BaseTestCase):

    def setUp(self):
        super(InstanceHandlerTest, self).setUp()

        self.controller = flexmock()
        self.retry = flexmock()
        self.instance_bus_adapter = instance_handler.InstanceHandler(self.controller)

    def test_deleted_instance(self):
        notification = messages.get_instance_delete_end_sample()

        self.controller.should_receive('delete_instance').once()
        self.instance_bus_adapter.on_instance_deleted(notification)

    def test_instance_resized(self):
        notification = messages.get_instance_rebuild_end_sample()

        self.controller.should_receive('resize_instance').once()
        self.instance_bus_adapter.on_instance_resized(notification)

    def test_instance_rebuild(self):
        notification = messages.get_instance_rebuild_end_sample()
        self.controller \
            .should_receive("rebuild_instance") \
            .once()
        self.instance_bus_adapter.on_instance_rebuilt(notification)
