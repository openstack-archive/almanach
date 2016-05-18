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

import unittest
from datetime import datetime

import pkg_resources
import mongomock
from flexmock import flexmock, flexmock_teardown
from hamcrest import assert_that, contains_inanyorder

from pymongo import MongoClient
import pytz

from almanach.adapters.database_adapter import DatabaseAdapter
from almanach.common.exceptions.volume_type_not_found_exception import VolumeTypeNotFoundException
from almanach.common.exceptions.almanach_exception import AlmanachException
from almanach import config
from almanach.core.model import todict
from tests.builder import a, instance, volume, volume_type


class DatabaseAdapterTest(unittest.TestCase):
    def setUp(self):
        config.read(pkg_resources.resource_filename("almanach", "resources/config/test.cfg"))
        mongo_connection = mongomock.Connection()

        self.adapter = DatabaseAdapter()
        self.db = mongo_connection[config.mongodb_database()]

        flexmock(MongoClient).new_instances(mongo_connection)

    def tearDown(self):
        flexmock_teardown()

    def test_insert_instance(self):
        fake_instance = a(instance())
        self.adapter.insert_entity(fake_instance)

        self.assertEqual(self.db.entity.count(), 1)
        self.assert_mongo_collection_contains("entity", fake_instance)

    def test_has_active_entity_not_found(self):
        self.assertFalse(self.adapter.has_active_entity("my_entity_id"))

    def test_has_active_entity_found(self):
        fake_instance = a(instance().with_id("my_entity_id"))
        self.adapter.insert_entity(fake_instance)
        self.assertTrue(self.adapter.has_active_entity("my_entity_id"))

    def test_get_instance_entity(self):
        fake_entity = a(instance().with_metadata({}))

        self.db.entity.insert(todict(fake_entity))

        self.assertEqual(self.adapter.get_active_entity(fake_entity.entity_id), fake_entity)

    def test_get_instance_entity_with_decode_output(self):
        fake_entity = a(instance().with_metadata({"a_metadata_not_sanitize": "not.sanitize",
                                                  "a_metadata^to_sanitize": "this.sanitize"}))

        self.db.entity.insert(todict(fake_entity))

        entity = self.adapter.get_active_entity(fake_entity.entity_id)

        expected_entity = a(instance()
                            .with_id(fake_entity.entity_id)
                            .with_project_id(fake_entity.project_id)
                            .with_metadata({"a_metadata_not_sanitize": "not.sanitize",
                                            "a_metadata.to_sanitize": "this.sanitize"}))

        self.assertEqual(entity, expected_entity)
        self.assert_entities_metadata_have_been_sanitize([entity])

    def test_get_instance_entity_will_not_found(self):
        with self.assertRaises(KeyError):
            self.adapter.get_active_entity("will_not_found")

    def test_get_instance_entity_with_unknown_type(self):
        fake_entity = a(instance())
        fake_entity.entity_type = "will_raise_excepion"

        self.db.entity.insert(todict(fake_entity))

        with self.assertRaises(NotImplementedError):
            self.adapter.get_active_entity(fake_entity.entity_id)

    def test_count_entities(self):
        fake_active_entities = [
            a(volume().with_id("id2").with_start(2014, 1, 1, 1, 0, 0).with_no_end()),
            a(instance().with_id("id3").with_start(2014, 1, 1, 8, 0, 0).with_no_end()),
        ]
        fake_inactive_entities = [
            a(instance().with_id("id1").with_start(2014, 1, 1, 7, 0, 0).with_end(2014, 1, 1, 8, 0, 0)),
            a(volume().with_id("id2").with_start(2014, 1, 1, 1, 0, 0).with_end(2014, 1, 1, 8, 0, 0)),
        ]
        [self.db.entity.insert(todict(fake_entity)) for fake_entity in fake_active_entities + fake_inactive_entities]

        self.assertEqual(4, self.adapter.count_entities())
        self.assertEqual(2, self.adapter.count_active_entities())
        self.assertEqual(1, self.adapter.count_entity_entries("id1"))
        self.assertEqual(2, self.adapter.count_entity_entries("id2"))

    def test_list_instances(self):
        fake_instances = [
            a(instance().with_id("id1").with_start(2014, 1, 1, 7, 0, 0).with_end(
                2014, 1, 1, 8, 0, 0).with_project_id("project_id").with_metadata({})),
            a(instance().with_id("id2").with_start(2014, 1, 1, 1, 0,
                                                   0).with_no_end().with_project_id("project_id").with_metadata({})),
            a(instance().with_id("id3").with_start(2014, 1, 1, 8, 0,
                                                   0).with_no_end().with_project_id("project_id").with_metadata({})),
        ]
        fake_volumes = [
            a(volume().with_id("id1").with_start(2014, 1, 1, 7, 0, 0).with_end(
                2014, 1, 1, 8, 0, 0).with_project_id("project_id")),
            a(volume().with_id("id2").with_start(2014, 1, 1, 1, 0, 0).with_no_end().with_project_id("project_id")),
            a(volume().with_id("id3").with_start(2014, 1, 1, 8, 0, 0).with_no_end().with_project_id("project_id")),
        ]
        [self.db.entity.insert(todict(fake_entity)) for fake_entity in fake_instances + fake_volumes]

        entities = self.adapter.list_entities("project_id", datetime(
            2014, 1, 1, 0, 0, 0, tzinfo=pytz.utc), datetime(2014, 1, 1, 12, 0, 0, tzinfo=pytz.utc), "instance")
        assert_that(entities, contains_inanyorder(*fake_instances))

    def test_list_instances_with_decode_output(self):
        fake_instances = [
            a(instance()
              .with_id("id1")
              .with_start(2014, 1, 1, 7, 0, 0)
              .with_end(2014, 1, 1, 8, 0, 0)
              .with_project_id("project_id")
              .with_metadata({"a_metadata_not_sanitize": "not.sanitize",
                              "a_metadata^to_sanitize": "this.sanitize"})),
            a(instance()
              .with_id("id2")
              .with_start(2014, 1, 1, 1, 0, 0)
              .with_no_end()
              .with_project_id("project_id")
              .with_metadata({"a_metadata^to_sanitize": "this.sanitize"})),
        ]

        expected_instances = [
            a(instance()
              .with_id("id1")
              .with_start(2014, 1, 1, 7, 0, 0)
              .with_end(2014, 1, 1, 8, 0, 0)
              .with_project_id("project_id")
              .with_metadata({"a_metadata_not_sanitize": "not.sanitize",
                              "a_metadata.to_sanitize": "this.sanitize"})),
            a(instance()
              .with_id("id2")
              .with_start(2014, 1, 1, 1, 0, 0)
              .with_no_end()
              .with_project_id("project_id")
              .with_metadata({"a_metadata.to_sanitize": "this.sanitize"})),
        ]

        [self.db.entity.insert(todict(fake_entity)) for fake_entity in fake_instances]

        entities = self.adapter.list_entities("project_id", datetime(
            2014, 1, 1, 0, 0, 0, tzinfo=pytz.utc), datetime(2014, 1, 1, 12, 0, 0, tzinfo=pytz.utc), "instance")
        assert_that(entities, contains_inanyorder(*expected_instances))
        self.assert_entities_metadata_have_been_sanitize(entities)

    def test_list_entities_in_period(self):
        fake_entities_in_period = [
            a(instance().with_id("in_the_period").with_start(2014, 1, 1, 7, 0,
                                                             0).with_end(2014, 1, 1, 8, 0, 0).with_project_id(
                "project_id")),
            a(instance().with_id("running_has_started_before").with_start(
                2014, 1, 1, 1, 0, 0).with_no_end().with_project_id("project_id")),
            a(instance().with_id("running_has_started_during").with_start(
                2014, 1, 1, 8, 0, 0).with_no_end().with_project_id("project_id")),
        ]
        fake_entities_out_period = [
            a(instance().with_id("before_the_period").with_start(2014, 1, 1, 0,
                                                                 0, 0).with_end(2014, 1, 1, 1, 0, 0).with_project_id(
                "project_id")),
            a(instance().with_id("after_the_period").with_start(2014, 1, 1, 10,
                                                                0, 0).with_end(2014, 1, 1, 11, 0, 0).with_project_id(
                "project_id")),
            a(instance().with_id("running_has_started_after").with_start(
                2014, 1, 1, 10, 0, 0).with_no_end().with_project_id("project_id")),
        ]
        [self.db.entity.insert(todict(fake_entity))
         for fake_entity in fake_entities_in_period + fake_entities_out_period]

        entities = self.adapter.list_entities("project_id", datetime(
            2014, 1, 1, 6, 0, 0, tzinfo=pytz.utc), datetime(2014, 1, 1, 9, 0, 0, tzinfo=pytz.utc))
        assert_that(entities, contains_inanyorder(*fake_entities_in_period))

    def test_list_entities_by_id(self):
        start = datetime(2016, 3, 1, 0, 0, 0, 0, pytz.utc)
        end = datetime(2016, 3, 3, 0, 0, 0, 0, pytz.utc)
        proper_instance = a(instance().with_id("id1").with_start(2016, 3, 1, 0, 0, 0).with_end(2016, 3, 2, 0, 0, 0))
        instances = [
            proper_instance,
            a(instance()
              .with_id("id1")
              .with_start(2016, 3, 2, 0, 0, 0)
              .with_no_end()),
        ]
        [self.db.entity.insert(todict(fake_instance)) for fake_instance in instances]

        instance_list = self.adapter.list_entities_by_id("id1", start, end)

        assert_that(instance_list, contains_inanyorder(*[proper_instance]))

    def test_update_active_entity(self):
        fake_entity = a(instance())
        end_date = datetime(2015, 10, 21, 16, 29, 0)

        self.db.entity.insert(todict(fake_entity))
        self.adapter.close_active_entity(fake_entity.entity_id, end_date)

        self.assertEqual(self.db.entity.find_one({"entity_id": fake_entity.entity_id})["end"], end_date)

    def test_update_closed_entity(self):
        fake_entity = a(instance().with_end(2016, 3, 2, 0, 0, 0))

        self.db.entity.insert(todict(fake_entity))
        fake_entity.flavor = "my_new_flavor"
        self.adapter.update_closed_entity(fake_entity, data={"flavor": fake_entity.flavor})

        db_entity = self.db.entity.find_one({"entity_id": fake_entity.entity_id})
        assert_that(db_entity['flavor'], fake_entity.flavor)
        assert_that(db_entity['end'], fake_entity.end)

    def test_replace_entity(self):
        fake_entity = a(instance())
        fake_entity.os.distro = "Centos"

        self.db.entity.insert(todict(fake_entity))
        fake_entity.os.distro = "Windows"

        self.adapter.update_active_entity(fake_entity)

        self.assertEqual(self.db.entity.find_one({"entity_id": fake_entity.entity_id})[
                             "os"]["distro"], fake_entity.os.distro)

    def test_insert_volume(self):
        count = self.db.entity.count()
        fake_volume = a(volume())
        self.adapter.insert_entity(fake_volume)

        self.assertEqual(count + 1, self.db.entity.count())
        self.assert_mongo_collection_contains("entity", fake_volume)

    def test_delete_active_entity(self):
        fake_entity = a(volume())

        self.db.entity.insert(todict(fake_entity))
        self.assertEqual(1, self.db.entity.count())

        self.adapter.delete_active_entity(fake_entity.entity_id)
        self.assertEqual(0, self.db.entity.count())

    def test_insert_volume_type(self):
        fake_volume_type = a(volume_type())
        self.adapter.insert_volume_type(fake_volume_type)

        self.assertEqual(1, self.db.volume_type.count())
        self.assert_mongo_collection_contains("volume_type", fake_volume_type)

    def test_get_volume_type(self):
        fake_volume_type = a(volume_type())
        self.db.volume_type.insert(todict(fake_volume_type))
        self.assertEqual(self.adapter.get_volume_type(fake_volume_type.volume_type_id), fake_volume_type)

    def test_get_volume_type_not_exist(self):
        fake_volume_type = a(volume_type())

        with self.assertRaises(VolumeTypeNotFoundException):
            self.adapter.get_volume_type(fake_volume_type.volume_type_id)

    def test_delete_volume_type(self):
        fake_volume_type = a(volume_type())
        self.db.volume_type.insert(todict(fake_volume_type))
        self.assertEqual(1, self.db.volume_type.count())
        self.adapter.delete_volume_type(fake_volume_type.volume_type_id)
        self.assertEqual(0, self.db.volume_type.count())

    def test_delete_volume_type_not_in_database(self):
        with self.assertRaises(AlmanachException):
            self.adapter.delete_volume_type("not_in_database_id")

    def test_delete_all_volume_types_not_permitted(self):
        with self.assertRaises(AlmanachException):
            self.adapter.delete_volume_type(None)

    def test_list_volume_types(self):
        fake_volume_types = [a(volume_type()), a(volume_type())]

        for fake_volume_type in fake_volume_types:
            self.db.volume_type.insert(todict(fake_volume_type))

        self.assertEqual(len(self.adapter.list_volume_types()), 2)

    def assert_mongo_collection_contains(self, collection, obj):
        (self.assertTrue(obj.as_dict() in self.db[collection].find(fields={"_id": 0}),
                         "The collection '%s' does not contains the object of type '%s'" % (collection, type(obj))))

    def assert_entities_metadata_have_been_sanitize(self, entities):
        for entity in entities:
            for key in entity.metadata:
                self.assertTrue(key.find("^") == -1,
                                "The metadata key %s contains carret" % (key))
