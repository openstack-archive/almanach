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


class VolumeHandler(base_handler.BaseHandler):

    def __init__(self, controller):
        super(VolumeHandler, self).__init__()
        self.controller = controller

    def handle_events(self, notification):
        if notification.event_type == "volume.create.end":
            self._on_volume_created(notification)
        elif notification.event_type == "volume.delete.end":
            self._on_volume_deleted(notification)
        elif notification.event_type == "volume.resize.end":
            self._on_volume_resized(notification)
        elif notification.event_type == "volume.attach.end":
            self._on_volume_attached(notification)
        elif notification.event_type == "volume.detach.end":
            self._on_volume_detached(notification)
        elif notification.event_type == "volume.update.end":
            self._on_volume_renamed(notification)
        elif notification.event_type == "volume.exists":
            self._on_volume_renamed(notification)

    def _on_volume_created(self, notification):
        date = notification.payload.get("created_at")
        project_id = notification.payload.get("tenant_id")
        volume_id = notification.payload.get("volume_id")
        volume_name = notification.payload.get("display_name")
        volume_type = notification.payload.get("volume_type")
        volume_size = notification.payload.get("size")
        self.controller.create_volume(volume_id, project_id, date, volume_type, volume_size, volume_name)

    def _on_volume_deleted(self, notification):
        volume_id = notification.payload.get("volume_id")
        end_date = notification.context.get("timestamp")
        self.controller.delete_volume(volume_id, end_date)

    def _on_volume_renamed(self, notification):
        volume_id = notification.payload.get("volume_id")
        volume_name = notification.payload.get("display_name")
        self.controller.rename_volume(volume_id, volume_name)

    def _on_volume_resized(self, notification):
        date = notification.context.get("timestamp")
        volume_id = notification.payload.get("volume_id")
        volume_size = notification.payload.get("size")
        self.controller.resize_volume(volume_id, volume_size, date)

    def _on_volume_attached(self, notification):
        volume_id = notification.payload.get("volume_id")
        event_date = notification.context.get("timestamp")
        self.controller.attach_volume(volume_id, event_date, self._get_attached_instances(notification))

    def _on_volume_detached(self, notification):
        volume_id = notification.payload.get("volume_id")
        event_date = notification.context.get("timestamp")
        self.controller.detach_volume(volume_id, event_date, self._get_attached_instances(notification))

    @staticmethod
    def _get_attached_instances(notification):
        instances_ids = []
        if "volume_attachment" in notification.payload:
            for instance in notification.payload["volume_attachment"]:
                instances_ids.append(instance.get("instance_uuid"))
        elif notification.payload.get("instance_uuid") is not None:
            instances_ids.append(notification.payload.get("instance_uuid"))
        return instances_ids
