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

from almanach.core import exception
from almanach.core import model

from almanach.tests.unit import base


class TestModel(base.BaseTestCase):

    def test_instance_serialize(self):
        instance = model.Instance(
            entity_id='instance_id',
            project_id='project_id',
            start=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            end=None,
            flavor='flavor_id',
            image_meta=dict(os_type='linux', distro='Ubuntu', version='16.04'),
            last_event=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            name='hostname',
            metadata={'some_key': 'some.value', 'another^key': 'another.value'},
        )

        entry = instance.as_dict()
        self.assertEqual('instance_id', entry['entity_id'])
        self.assertEqual('project_id', entry['project_id'])
        self.assertEqual('instance', entry['entity_type'])
        self.assertEqual('hostname', entry['name'])
        self.assertEqual('flavor_id', entry['flavor'])
        self.assertEqual('linux', entry['os']['os_type'])
        self.assertEqual('Ubuntu', entry['os']['distro'])
        self.assertEqual('16.04', entry['os']['version'])
        self.assertEqual('linux', entry['image_meta']['os_type'])
        self.assertEqual('Ubuntu', entry['image_meta']['distro'])
        self.assertEqual('16.04', entry['image_meta']['version'])
        self.assertEqual(datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc), entry['last_event'])
        self.assertEqual(datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc), entry['start'])
        self.assertIsNone(entry['end'])

    def test_instance_unserialize(self):
        entry = {
            'entity_id': 'instance_id',
            'entity_type': 'instance',
            'project_id': 'project_id',
            'start': datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            'end': None,
            'last_event': datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            'flavor': 'flavor_id',
            'image_meta': {
                'os_type': 'linux',
                'distro': 'Ubuntu',
                'version': '16.04',
            },
            'name': 'hostname'
        }

        instance = model.get_entity_from_dict(entry)
        self.assertEqual('instance_id', instance.entity_id)
        self.assertEqual('project_id', instance.project_id)
        self.assertEqual('instance', instance.entity_type)
        self.assertEqual('hostname', instance.name)
        self.assertEqual('flavor_id', instance.flavor)
        self.assertEqual('linux', instance.image_meta['os_type'])
        self.assertEqual('Ubuntu', instance.image_meta['distro'])
        self.assertEqual('16.04', instance.image_meta['version'])
        self.assertEqual(datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc), instance.last_event)
        self.assertEqual(datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc), instance.start)
        self.assertIsNone(instance.end)

    def test_instance_unserialize_with_legacy_os(self):
        entry = {
            'entity_id': 'instance_id',
            'entity_type': 'instance',
            'project_id': 'project_id',
            'start': datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            'end': None,
            'last_event': datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            'flavor': 'flavor_id',
            'os': {
                'os_type': 'linux',
                'distro': 'Ubuntu',
                'version': '16.04',
            },
            'name': 'hostname'
        }

        instance = model.get_entity_from_dict(entry)
        self.assertEqual('instance_id', instance.entity_id)
        self.assertEqual('project_id', instance.project_id)
        self.assertEqual('instance', instance.entity_type)
        self.assertEqual('hostname', instance.name)
        self.assertEqual('flavor_id', instance.flavor)
        self.assertEqual('linux', instance.image_meta['os_type'])
        self.assertEqual('Ubuntu', instance.image_meta['distro'])
        self.assertEqual('16.04', instance.image_meta['version'])
        self.assertEqual(datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc), instance.last_event)
        self.assertEqual(datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc), instance.start)
        self.assertIsNone(instance.end)

    def test_instance_unserialize_with_both_keys(self):
        entry = {
            'entity_id': 'instance_id',
            'entity_type': 'instance',
            'project_id': 'project_id',
            'start': datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            'end': None,
            'last_event': datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            'flavor': 'flavor_id',
            'os': {
                'os_type': 'linux',
                'distro': 'Ubuntu',
                'version': '16.04',
            },
            'image_meta': {
                'os_type': 'linux',
                'distro': 'Ubuntu',
                'version': '16.04',
            },
            'name': 'hostname'
        }

        instance = model.get_entity_from_dict(entry)
        self.assertEqual('instance_id', instance.entity_id)
        self.assertEqual('project_id', instance.project_id)
        self.assertEqual('instance', instance.entity_type)
        self.assertEqual('hostname', instance.name)
        self.assertEqual('flavor_id', instance.flavor)
        self.assertEqual('linux', instance.image_meta['os_type'])
        self.assertEqual('Ubuntu', instance.image_meta['distro'])
        self.assertEqual('16.04', instance.image_meta['version'])
        self.assertEqual(datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc), instance.last_event)
        self.assertEqual(datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc), instance.start)
        self.assertIsNone(instance.end)

    def test_instance_comparison(self):
        instance1 = model.Instance(
            entity_id='instance_id',
            project_id='project_id',
            start=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            end=None,
            flavor='flavor_id',
            image_meta=dict(os_type='linux', distro='Ubuntu', version='16.04'),
            last_event=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            name='hostname',
            metadata={'some_key': 'some.value', 'another^key': 'another.value'},
        )

        instance2 = model.Instance(
            entity_id='instance_id',
            project_id='project_id',
            start=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            end=None,
            flavor='flavor_id',
            image_meta=dict(os_type='linux', distro='Ubuntu', version='16.04'),
            last_event=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            name='hostname',
            metadata={'some_key': 'some.value', 'another^key': 'another.value'},
        )

        # different image properties
        instance3 = model.Instance(
            entity_id='instance_id',
            project_id='project_id',
            start=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            end=None,
            flavor='flavor_id',
            image_meta=dict(os_type='linux', distro='Centos', version='7'),
            last_event=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            name='hostname',
            metadata={'some_key': 'some.value', 'another^key': 'another.value'},
        )

        # different flavor
        instance4 = model.Instance(
            entity_id='instance_id',
            project_id='project_id',
            start=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            end=None,
            flavor='another_flavor',
            image_meta=dict(os_type='linux', distro='Ubuntu', version='16.04'),
            last_event=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            name='hostname',
            metadata={'some_key': 'some.value', 'another^key': 'another.value'},
        )

        # different metadata
        instance5 = model.Instance(
            entity_id='instance_id',
            project_id='project_id',
            start=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            end=None,
            flavor='flavor_id',
            image_meta=dict(os_type='linux', distro='Ubuntu', version='16.04'),
            last_event=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            name='hostname',
            metadata=dict(),
        )

        self.assertTrue(instance1 == instance2)
        self.assertTrue(instance1 != instance3)
        self.assertTrue(instance1 != instance4)
        self.assertTrue(instance1 != instance5)

    def test_volume_serialize(self):
        volume = model.Volume(
            entity_id='volume_id',
            project_id='project_id',
            start=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            end=None,
            last_event=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            name='volume_name',
            volume_type='volume_type_id',
            size=2,
            attached_to=['instance_id1', 'instance_id2'],
        )

        entry = volume.as_dict()
        self.assertEqual('volume_id', entry['entity_id'])
        self.assertEqual('project_id', entry['project_id'])
        self.assertEqual('volume', entry['entity_type'])
        self.assertEqual('volume_name', entry['name'])
        self.assertEqual('volume_type_id', entry['volume_type'])
        self.assertEqual(2, entry['size'])
        self.assertEqual(['instance_id1', 'instance_id2'], entry['attached_to'])
        self.assertEqual(datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc), entry['last_event'])
        self.assertEqual(datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc), entry['start'])
        self.assertIsNone(entry['end'])

    def test_volume_unserialize(self):
        entry = {
            'entity_id': 'volume_id',
            'entity_type': 'volume',
            'project_id': 'project_id',
            'start': datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            'end': None,
            'last_event': datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            'volume_type': 'volume_type_id',
            'name': 'volume_name',
            'size': 2,
        }

        volume = model.get_entity_from_dict(entry)
        self.assertEqual('volume_id', volume.entity_id)
        self.assertEqual('project_id', volume.project_id)
        self.assertEqual('volume', volume.entity_type)
        self.assertEqual('volume_name', volume.name)
        self.assertEqual(2, volume.size)
        self.assertEqual([], volume.attached_to)
        self.assertEqual(datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc), volume.last_event)
        self.assertEqual(datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc), volume.start)
        self.assertIsNone(volume.end)

    def test_volume_comparison(self):
        volume1 = model.Volume(
            entity_id='volume_id',
            project_id='project_id',
            start=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            end=None,
            last_event=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            name='volume_name',
            volume_type='volume_type_id',
            size=2,
            attached_to=['instance_id1', 'instance_id2'],
        )

        volume2 = model.Volume(
            entity_id='volume_id',
            project_id='project_id',
            start=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            end=None,
            last_event=datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc),
            name='volume_name',
            volume_type='volume_type_id',
            size=2,
            attached_to=['instance_id1', 'instance_id2'],
        )

        self.assertTrue(volume1 == volume2)

        volume2.volume_type = 'another_volume_type'
        self.assertFalse(volume1 == volume2)

        volume2.volume_type = 'volume_type_id'
        volume2.size = 3
        self.assertFalse(volume1 == volume2)

        volume2.volume_type = 'volume_type_id'
        volume2.size = 2
        volume2.attached_to = []
        self.assertFalse(volume1 == volume2)

    def test_volume_type_serialize(self):
        volume_type = model.VolumeType(
            volume_type_id='id',
            volume_type_name='name',
        )

        entry = volume_type.as_dict()
        self.assertEqual('id', entry['volume_type_id'])
        self.assertEqual('name', entry['volume_type_name'])

    def test_volume_type_unserialize(self):
        entry = dict(volume_type_id='id', volume_type_name='name')

        volume_type = model.VolumeType.from_dict(entry)
        self.assertEqual('id', volume_type.volume_type_id)
        self.assertEqual('name', volume_type.volume_type_name)

    def test_volume_type_comparison(self):
        volume_type1 = model.VolumeType(volume_type_id='id', volume_type_name='name')
        volume_type2 = model.VolumeType(volume_type_id='id2', volume_type_name='name2')
        volume_type3 = model.VolumeType(volume_type_id='id', volume_type_name='name')

        self.assertTrue(volume_type1 != volume_type2)
        self.assertTrue(volume_type1 == volume_type3)

    def test_unserialize_unknown_entity(self):
        self.assertRaises(exception.EntityTypeNotSupportedException,
                          model.get_entity_from_dict,
                          dict(entity_type='unknown'))
