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


class Entity(object):
    def __init__(self, entity_id, project_id, start, end, last_event, name, entity_type):
        self.entity_id = entity_id
        self.project_id = project_id
        self.start = start
        self.end = end
        self.last_event = last_event
        self.name = name
        self.entity_type = entity_type

    def as_dict(self):
        return todict(self)

    def __eq__(self, other):
        return (other.entity_id == self.entity_id and
                other.project_id == self.project_id and
                other.start == self.start and
                other.end == self.end and
                other.last_event == self.last_event and
                other.name == self.name and
                other.entity_type == self.entity_type)


class Instance(Entity):
    TYPE = "instance"

    def __init__(self, entity_id, project_id, start, end, flavor, os, last_event, name, metadata={}, entity_type=TYPE):
        super(Instance, self).__init__(entity_id, project_id, start, end, last_event, name, entity_type)
        self.flavor = flavor
        self.metadata = metadata
        self.os = OS(**os)

    def __eq__(self, other):
        return (super(Instance, self).__eq__(other) and
                other.flavor == self.flavor and
                other.os == self.os and
                other.metadata == self.metadata)


class OS(object):
    def __init__(self, os_type, distro, version):
        self.os_type = os_type
        self.distro = distro
        self.version = version

    def __eq__(self, other):
        return (other.os_type == self.os_type and
                other.distro == self.distro and
                other.version == self.version)


class Volume(Entity):
    TYPE = "volume"

    def __init__(self, entity_id, project_id, start, end, volume_type, size, last_event, name, attached_to=None,
                 entity_type=TYPE):
        super(Volume, self).__init__(entity_id, project_id, start, end, last_event, name, entity_type)
        self.volume_type = volume_type
        self.size = size
        self.attached_to = attached_to or []

    def __eq__(self, other):
        return (super(Volume, self).__eq__(other) and
                other.volume_type == self.volume_type and
                other.size == self.size and
                other.attached_to == self.attached_to)


class VolumeType(object):
    def __init__(self, volume_type_id, volume_type_name):
        self.volume_type_id = volume_type_id
        self.volume_type_name = volume_type_name

    def __eq__(self, other):
        return other.__dict__ == self.__dict__

    def as_dict(self):
        return todict(self)


def build_entity_from_dict(entity_dict):
    if entity_dict.get("entity_type") == Instance.TYPE:
        return Instance(**entity_dict)
    elif entity_dict.get("entity_type") == Volume.TYPE:
        return Volume(**entity_dict)
    raise NotImplementedError("unsupported entity type: '%s'" % entity_dict.get("entity_type"))


def todict(obj):
    if isinstance(obj, dict):
        return obj
    elif hasattr(obj, "__iter__"):
        return [todict(v) for v in obj]
    elif hasattr(obj, "__dict__"):
        return dict([(key, todict(value))
                     for key, value in obj.__dict__.iteritems()
                     if not callable(value) and not key.startswith('_')])
    else:
        return obj
