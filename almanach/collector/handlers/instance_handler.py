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

from oslo_log import log as logging

from almanach.collector.handlers import base_handler
from almanach.core import exception

LOG = logging.getLogger(__name__)


class InstanceHandler(base_handler.BaseHandler):

    def __init__(self, controller, on_delete_filter):
        super(InstanceHandler, self).__init__()
        self.controller = controller
        self.on_delete_filter = on_delete_filter

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
            instance_id=notification.payload.get("instance_id"),
            tenant_id=notification.payload.get("tenant_id"),
            create_date=notification.payload.get("created_at"),
            name=notification.payload.get("hostname"),
            flavor=notification.payload.get("instance_type"),
            image_meta=notification.payload.get("image_meta"),
            metadata=notification.payload.get("metadata"),
        )

    def _on_instance_deleted(self, notification):
        date = notification.payload.get("terminated_at")
        instance_id = notification.payload.get("instance_id")

        try:
            self.controller.delete_instance(instance_id, date)
        except exception.EntityNotFoundException as e:
            if not self.on_delete_filter.ignore_notification(notification):
                raise e

    def _on_instance_resized(self, notification):
        date = notification.context.get("timestamp")
        flavor = notification.payload.get("instance_type")
        instance_id = notification.payload.get("instance_id")
        self.controller.resize_instance(instance_id, flavor, date)

    def _on_instance_rebuilt(self, notification):
        date = notification.context.get("timestamp")
        instance_id = notification.payload.get("instance_id")
        self.controller.rebuild_instance(
            instance_id=instance_id,
            rebuild_date=date,
            image_meta=notification.payload.get("image_meta")
        )
