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

import pytz

from copy import copy
from datetime import datetime
from uuid import uuid4

from almanach.core.model import build_entity_from_dict, Instance, Volume, VolumeType


class Builder(object):

    def __init__(self, dict_object):
        self.dict_object = dict_object


class EntityBuilder(Builder):

    def build(self):
        return build_entity_from_dict(self.dict_object)

    def with_id(self, entity_id):
        self.dict_object["entity_id"] = entity_id
        return self

    def with_project_id(self, project_id):
        self.dict_object["project_id"] = project_id
        return self

    def with_last_event(self, last_event):
        self.dict_object["last_event"] = last_event
        return self

    def with_start(self, year, month, day, hour, minute, second):
        self.with_datetime_start(datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc))
        return self

    def with_datetime_start(self, date):
        self.dict_object["start"] = date
        return self

    def with_end(self, year, month, day, hour, minute, second):
        self.dict_object["end"] = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
        return self

    def with_no_end(self):
        self.dict_object["end"] = None
        return self

    def with_flavor(self, flavor):
        self.dict_object["flavor"] = flavor
        return self

    def with_metadata(self, metadata):
        self.dict_object['metadata'] = metadata
        return self

    def build_from(self, other):
        self.dict_object = copy(other.__dict__)
        return self

    def with_all_dates_in_string(self):
        self.dict_object['start'] = self.dict_object['start'].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.dict_object['last_event'] = self.dict_object['last_event'].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return self


class VolumeBuilder(EntityBuilder):

    def with_attached_to(self, attached_to):
        self.dict_object["attached_to"] = attached_to
        return self

    def with_no_attachment(self):
        self.dict_object["attached_to"] = []
        return self

    def with_display_name(self, display_name):
        self.dict_object["name"] = display_name
        return self

    def with_volume_type(self, volume_type):
        self.dict_object["volume_type"] = volume_type
        return self


class VolumeTypeBuilder(Builder):

    def build(self):
        return VolumeType(**self.dict_object)

    def with_volume_type_id(self, volume_type_id):
        self.dict_object["volume_type_id"] = volume_type_id
        return self

    def with_volume_type_name(self, volume_type_name):
        self.dict_object["volume_type_name"] = volume_type_name
        return self


def instance():
    return EntityBuilder({
        "entity_id": str(uuid4()),
        "project_id": str(uuid4()),
        "start": datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
        "end": None,
        "last_event": datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
        "flavor": "A1.1",
        "os": {
            "os_type": "windows",
            "distro": "windows",
            "version": "2012r2"
        },
        "entity_type": Instance.TYPE,
        "name": "some-instance",
        "metadata": {
            "a_metadata.to_filter": "include.this",
            "a_metadata.to_exclude": "exclude.this"
        }
    })


def volume():
    return VolumeBuilder({
        "entity_id": str(uuid4()),
        "project_id": str(uuid4()),
        "start": datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
        "end": None,
        "last_event": datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
        "volume_type": "SF400",
        "size": 1000000,
        "entity_type": Volume.TYPE,
        "name": "some-volume",
        "attached_to": None,
    })


def volume_type():
    return VolumeTypeBuilder({
        "volume_type_id": str(uuid4()),
        "volume_type_name": "a_type_name"
    })


def a(builder):
    return builder.build()
