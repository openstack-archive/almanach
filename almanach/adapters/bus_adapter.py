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

import json
import logging
import kombu

from kombu.mixins import ConsumerMixin
from almanach import config


class BusAdapter(ConsumerMixin):

    def __init__(self, controller, connection, retry_adapter):
        super(BusAdapter, self).__init__()
        self.controller = controller
        self.connection = connection
        self.retry_adapter = retry_adapter

    def on_message(self, notification, message):
        try:
            self._process_notification(notification)
        except Exception as e:
            logging.warning("Sending notification to retry letter exchange {0}".format(json.dumps(notification)))
            logging.exception(e.message)
            self.retry_adapter.publish_to_dead_letter(message)
        message.ack()

    def _process_notification(self, notification):
        if isinstance(notification, basestring):
            notification = json.loads(notification)

        event_type = notification.get("event_type")
        logging.info(event_type)

        if event_type == "compute.instance.create.end":
            self._instance_created(notification)
        elif event_type == "compute.instance.delete.end":
            self._instance_deleted(notification)
        elif event_type == "compute.instance.resize.confirm.end":
            self._instance_resized(notification)
        elif event_type == "compute.instance.rebuild.end":
            self._instance_rebuilt(notification)
        elif event_type == "volume.create.end":
            self._volume_created(notification)
        elif event_type == "volume.delete.end":
            self._volume_deleted(notification)
        elif event_type == "volume.resize.end":
            self._volume_resized(notification)
        elif event_type == "volume.attach.end":
            self._volume_attached(notification)
        elif event_type == "volume.detach.end":
            self._volume_detached(notification)
        elif event_type == "volume.update.end":
            self._volume_renamed(notification)
        elif event_type == "volume.exists":
            self._volume_renamed(notification)
        elif event_type == "volume_type.create":
            self._volume_type_create(notification)

    def get_consumers(self, consumer, channel):
        queue = kombu.Queue(config.rabbitmq_queue(), routing_key=config.rabbitmq_routing_key())
        return [consumer(
            [queue],
            callbacks=[self.on_message],
            auto_declare=False)]

    def run(self, _tokens=1):
        try:
            super(BusAdapter, self).run(_tokens)
        except KeyboardInterrupt:
            pass

    def _instance_created(self, notification):
        payload = notification.get("payload")
        project_id = payload.get("tenant_id")
        date = payload.get("created_at")
        instance_id = payload.get("instance_id")
        flavor = payload.get("instance_type")
        os_type = payload.get("image_meta").get("os_type")
        distro = payload.get("image_meta").get("distro")
        version = payload.get("image_meta").get("version")
        name = payload.get("hostname")
        metadata = payload.get("metadata")
        if isinstance(metadata, list):
            metadata = {}
        self.controller.create_instance(
            instance_id,
            project_id,
            date,
            flavor,
            os_type,
            distro,
            version,
            name,
            metadata
        )

    def _instance_deleted(self, notification):
        payload = notification.get("payload")
        date = payload.get("terminated_at")
        instance_id = payload.get("instance_id")
        self.controller.delete_instance(instance_id, date)

    def _instance_resized(self, notification):
        payload = notification.get("payload")
        date = notification.get("timestamp")
        flavor = payload.get("instance_type")
        instance_id = payload.get("instance_id")
        self.controller.resize_instance(instance_id, flavor, date)

    def _volume_created(self, notification):
        payload = notification.get("payload")
        date = payload.get("created_at")
        project_id = payload.get("tenant_id")
        volume_id = payload.get("volume_id")
        volume_name = payload.get("display_name")
        volume_type = payload.get("volume_type")
        volume_size = payload.get("size")
        self.controller.create_volume(volume_id, project_id, date, volume_type, volume_size, volume_name)

    def _volume_deleted(self, notification):
        payload = notification.get("payload")
        volume_id = payload.get("volume_id")
        end_date = notification.get("timestamp")
        self.controller.delete_volume(volume_id, end_date)

    def _volume_renamed(self, notification):
        payload = notification.get("payload")
        volume_id = payload.get("volume_id")
        volume_name = payload.get("display_name")
        self.controller.rename_volume(volume_id, volume_name)

    def _volume_resized(self, notification):
        payload = notification.get("payload")
        date = notification.get("timestamp")
        volume_id = payload.get("volume_id")
        volume_size = payload.get("size")
        self.controller.resize_volume(volume_id, volume_size, date)

    def _volume_attached(self, notification):
        payload = notification.get("payload")
        volume_id = payload.get("volume_id")
        event_date = notification.get("timestamp")
        self.controller.attach_volume(volume_id, event_date, self._get_attached_instances(payload))

    def _volume_detached(self, notification):
        payload = notification.get("payload")
        volume_id = payload.get("volume_id")
        event_date = notification.get("timestamp")
        self.controller.detach_volume(volume_id, event_date, self._get_attached_instances(payload))

    @staticmethod
    def _get_attached_instances(payload):
        instances_ids = []
        if "volume_attachment" in payload:
            for instance in payload["volume_attachment"]:
                instances_ids.append(instance.get("instance_uuid"))
        elif payload.get("instance_uuid") is not None:
            instances_ids.append(payload.get("instance_uuid"))

        return instances_ids

    def _instance_rebuilt(self, notification):
        payload = notification.get("payload")
        date = notification.get("timestamp")
        instance_id = payload.get("instance_id")
        distro = payload.get("image_meta").get("distro")
        version = payload.get("image_meta").get("version")
        os_type = payload.get("image_meta").get("os_type")
        self.controller.rebuild_instance(instance_id, distro, version, os_type, date)

    def _volume_type_create(self, notification):
        volume_types = notification.get("payload").get("volume_types")
        volume_type_id = volume_types.get("id")
        volume_type_name = volume_types.get("name")
        self.controller.create_volume_type(volume_type_id, volume_type_name)
