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
import pytz

from almanach.collector import notification


class NotificationMessageBuilder(object):

    def __init__(self):
        self.event_type = None
        self.context = dict()
        self.payload = dict()
        self.metadata = dict()

    def with_event_type(self, event_type):
        self.event_type = event_type
        return self

    def with_context_value(self, key, value):
        self.context[key] = value
        return self

    def with_payload_value(self, key, value):
        self.payload[key] = value
        return self

    def build(self):
        return notification.NotificationMessage(self.event_type, self.context, self.payload, self.metadata)


class InstanceNotificationBuilder(NotificationMessageBuilder):

    def __init__(self):
        super(InstanceNotificationBuilder, self).__init__()
        self.payload = {
            'instance_id': 'my_instance_id',
            'tenant_id': 'my_tenant_id',
            'created_at': datetime(2014, 2, 14, 16, 29, 58, tzinfo=pytz.utc),
            'terminated_at': None,
            'instance_type': 'my_flavor_name',
            'image_meta': {},
            'hostname': 'my_instance_name',
            'metadata': {},
        }

    def with_image_meta(self, key, value):
        self.payload['image_meta'][key] = value
        return self


class VolumeTypeNotificationBuilder(NotificationMessageBuilder):

    def __init__(self):
        super(VolumeTypeNotificationBuilder, self).__init__()
        self.payload = {
            'volume_types': {
                'name': 'my_volume_type_name',
                "qos_specs_id": None,
                "deleted": False,
                "created_at": "2014-02-14T17:18:35.036186Z",
                "extra_specs": {},
                "deleted_at": None,
                "id": 'my_volume_type_id',
            }
        }


class VolumeNotificationBuilder(NotificationMessageBuilder):

    def __init__(self):
        super(VolumeNotificationBuilder, self).__init__()
        self.payload = {
            'created_at': '2015-07-27T16:11:07Z',
            'tenant_id': 'my_tenant_id',
            'volume_id': 'my_volume_id',
            'display_name': 'my_volume_name',
            'volume_type': 'my_volume_type',
            'size': 1,
            'volume_attachment': [],
        }

    def with_instance_attached(self, instance_id):
        self.payload['volume_attachment'].append({'instance_uuid': instance_id})
        return self
