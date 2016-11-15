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

from almanach.collector.handlers import base_handler


class VolumeTypeHandler(base_handler.BaseHandler):

    def __init__(self, controller):
        super(VolumeTypeHandler, self).__init__()
        self.controller = controller

    def handle_events(self, notification):
        if notification.event_type == "volume_type.create":
            self._on_volume_type_created(notification)

    def _on_volume_type_created(self, notification):
        volume_types = notification.payload.get("volume_types")
        volume_type_id = volume_types.get("id")
        volume_type_name = volume_types.get("name")
        self.controller.create_volume_type(volume_type_id, volume_type_name)
