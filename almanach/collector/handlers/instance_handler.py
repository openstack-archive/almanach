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


class InstanceHandler(base_handler.BaseHandler):

    def __init__(self, controller):
        super(InstanceHandler, self).__init__()
        self.controller = controller

    def handle_events(self, notification):
        if notification.event_type == "compute.instance.create.end":
            self._on_instance_created(notification)
        elif notification.event_type == "compute.instance.delete.end":
            self._on_instance_deleted(notification)
        elif notification.event_type == "compute.instance.resize.confirm.end":
            self._on_instance_resized(notification)
        elif notification.event_type == "compute.instance.rebuild.end":
            self._on_instance_rebuilt(notification)

    def _on_instance_created(self, notification):
        self.controller.create_instance(
            notification.payload.get("instance_id"),
            notification.payload.get("tenant_id"),
            notification.payload.get("created_at"),
            notification.payload.get("instance_type"),
            notification.payload.get("image_meta").get("os_type"),
            notification.payload.get("image_meta").get("distro"),
            notification.payload.get("image_meta").get("version"),
            notification.payload.get("hostname"),
            notification.metadata
        )

    def _on_instance_deleted(self, notification):
        date = notification.payload.get("terminated_at")
        instance_id = notification.payload.get("instance_id")
        self.controller.delete_instance(instance_id, date)

    def _on_instance_resized(self, notification):
        date = notification.context.get("timestamp")
        flavor = notification.payload.get("instance_type")
        instance_id = notification.payload.get("instance_id")
        self.controller.resize_instance(instance_id, flavor, date)

    def _on_instance_rebuilt(self, notification):
        date = notification.context.get("timestamp")
        instance_id = notification.payload.get("instance_id")
        distro = notification.payload.get("image_meta").get("distro")
        version = notification.payload.get("image_meta").get("version")
        os_type = notification.payload.get("image_meta").get("os_type")
        self.controller.rebuild_instance(instance_id, distro, version, os_type, date)
