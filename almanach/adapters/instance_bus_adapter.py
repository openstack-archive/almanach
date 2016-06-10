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


class InstanceBusAdapter(object):
    def __init__(self, controller):
        self.controller = controller

    def handle_events(self, event_type, notification):
        if event_type == "compute.instance.create.end":
            self.on_instance_created(notification)
        elif event_type == "compute.instance.delete.end":
            self.on_instance_deleted(notification)
        elif event_type == "compute.instance.resize.confirm.end":
            self.on_instance_resized(notification)
        elif event_type == "compute.instance.rebuild.end":
            self.on_instance_rebuilt(notification)

    def on_instance_created(self, notification):
        payload = notification.get("payload")
        metadata = payload.get("metadata")

        if isinstance(metadata, list):
            metadata = {}

        self.controller.create_instance(
            payload.get("instance_id"),
            payload.get("tenant_id"),
            payload.get("created_at"),
            payload.get("instance_type"),
            payload.get("image_meta").get("os_type"),
            payload.get("image_meta").get("distro"),
            payload.get("image_meta").get("version"),
            payload.get("hostname"),
            metadata
        )

    def on_instance_deleted(self, notification):
        payload = notification.get("payload")
        date = payload.get("terminated_at")
        instance_id = payload.get("instance_id")
        self.controller.delete_instance(instance_id, date)

    def on_instance_resized(self, notification):
        payload = notification.get("payload")
        date = notification.get("timestamp")
        flavor = payload.get("instance_type")
        instance_id = payload.get("instance_id")
        self.controller.resize_instance(instance_id, flavor, date)

    def on_instance_rebuilt(self, notification):
        payload = notification.get("payload")
        date = notification.get("timestamp")
        instance_id = payload.get("instance_id")
        distro = payload.get("image_meta").get("distro")
        version = payload.get("image_meta").get("version")
        os_type = payload.get("image_meta").get("os_type")
        self.controller.rebuild_instance(instance_id, distro, version, os_type, date)
