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

import abc
import six

from almanach.core import exception


@six.add_metaclass(abc.ABCMeta)
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
        return dict(
            entity_id=self.entity_id,
            project_id=self.project_id,
            start=self.start,
            end=self.end,
            last_event=self.last_event,
            name=self.name,
            entity_type=self.entity_type,
        )

    @staticmethod
    def from_dict(d):
        raise NotImplementedError

    def __eq__(self, other):
        return (other.entity_id == self.entity_id and
                other.project_id == self.project_id and
                other.start == self.start and
                other.end == self.end and
                other.last_event == self.last_event and
                other.name == self.name and
                other.entity_type == self.entity_type)

    def __ne__(self, other):
        return not self.__eq__(other)


class Instance(Entity):
    TYPE = 'instance'

    def __init__(self, entity_id, project_id, start, end, flavor, last_event, name, image_meta=None, metadata=None):
        super(Instance, self).__init__(entity_id, project_id, start, end, last_event, name, self.TYPE)
        self.flavor = flavor
        self.metadata = metadata or dict()
        self.image_meta = image_meta or dict()

        # TODO(fguillot): This attribute still used by the legacy API,
        # that should be removed when the new API v2 will be implemented
        self.os = self.image_meta

    def __eq__(self, other):
        return (super(Instance, self).__eq__(other) and
                other.flavor == self.flavor and
                other.image_meta == self.image_meta and
                other.metadata == self.metadata)

    def as_dict(self):
        d = super(Instance, self).as_dict()
        d['flavor'] = self.flavor
        d['metadata'] = self.metadata
        d['image_meta'] = self.image_meta

        # NOTE(fguillot): we keep this key for backward compatibility
        d['os'] = self.image_meta
        return d

    @staticmethod
    def from_dict(d):
        return Instance(
            entity_id=d.get('entity_id'),
            project_id=d.get('project_id'),
            start=d.get('start'),
            end=d.get('end'),
            last_event=d.get('last_event'),
            name=d.get('name'),
            flavor=d.get('flavor'),
            image_meta=d.get('os') or d.get('image_meta'),
            metadata=Instance._unserialize_metadata(d),
        )

    @staticmethod
    def _unserialize_metadata(d):
        metadata = d.get('metadata')
        if metadata:
            tmp = dict()
            for key, value in metadata.items():
                if '^' in key:
                    key = key.replace('^', '.')
                tmp[key] = value
            metadata = tmp
        return metadata

    def _serialize_metadata(self):
        tmp = dict()
        for key, value in self.metadata.items():
            if '.' in key:
                key = key.replace('.', '^')
            tmp[key] = value
        return tmp


class Volume(Entity):
    TYPE = 'volume'

    def __init__(self, entity_id, project_id, start, end, volume_type, size, last_event, name, attached_to=None):
        super(Volume, self).__init__(entity_id, project_id, start, end, last_event, name, self.TYPE)
        self.volume_type = volume_type
        self.size = size
        self.attached_to = attached_to or []

    def __eq__(self, other):
        return (super(Volume, self).__eq__(other) and
                other.volume_type == self.volume_type and
                other.size == self.size and
                other.attached_to == self.attached_to)

    def as_dict(self):
        d = super(Volume, self).as_dict()
        d['volume_type'] = self.volume_type
        d['size'] = self.size
        d['attached_to'] = self.attached_to
        return d

    @staticmethod
    def from_dict(d):
        return Volume(
            entity_id=d.get('entity_id'),
            project_id=d.get('project_id'),
            start=d.get('start'),
            end=d.get('end'),
            last_event=d.get('last_event'),
            name=d.get('name'),
            volume_type=d.get('volume_type'),
            size=d.get('size'),
            attached_to=d.get('attached_to'),
        )


class VolumeType(object):

    def __init__(self, volume_type_id, volume_type_name):
        self.volume_type_id = volume_type_id
        self.volume_type_name = volume_type_name

    def __eq__(self, other):
        return other.__dict__ == self.__dict__

    def as_dict(self):
        return dict(
            volume_type_id=self.volume_type_id,
            volume_type_name=self.volume_type_name,
        )

    @staticmethod
    def from_dict(d):
        return VolumeType(volume_type_id=d['volume_type_id'],
                          volume_type_name=d['volume_type_name'])


def get_entity_from_dict(d):
    entity_type = d.get('entity_type')
    if entity_type == Instance.TYPE:
        return Instance.from_dict(d)
    elif entity_type == Volume.TYPE:
        return Volume.from_dict(d)
    raise exception.EntityTypeNotSupportedException(
            'Unsupported entity type: "{}"'.format(entity_type))
