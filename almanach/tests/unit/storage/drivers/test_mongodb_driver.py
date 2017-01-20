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

import mongomock
import pytz

from almanach.core import exception
from almanach.core import model
from almanach.storage.drivers import mongodb_driver

from almanach.tests.unit import base
from almanach.tests.unit.builders.entity import a
from almanach.tests.unit.builders.entity import instance
from almanach.tests.unit.builders.entity import volume
from almanach.tests.unit.builders.entity import volume_type


class TestMongoDbDriver(base.BaseTestCase):

    def setUp(self):
        super(TestMongoDbDriver, self).setUp()
        mongo_connection = mongomock.Connection()
        self.db = mongo_connection['almanach']
        self.adapter = mongodb_driver.MongoDbDriver(self.config, self.db)

    def test_insert_instance_entity(self):
        fake_instance = a(instance())
        self.adapter.insert_entity(fake_instance)
        self.assertEqual(self.db.entity.count(), 1)
        self.assert_mongo_collection_contains("entity", fake_instance)

    def test_insert_volume_entity(self):
        count = self.db.entity.count()
        fake_volume = a(volume())
        self.adapter.insert_entity(fake_volume)

        self.assertEqual(count + 1, self.db.entity.count())
        self.assert_mongo_collection_contains("entity", fake_volume)

    def test_has_active_entity_not_found(self):
        self.assertFalse(self.adapter.has_active_entity("my_entity_id"))

    def test_has_active_entity_found(self):
        fake_instance = a(instance().with_id("my_entity_id"))
        self.adapter.insert_entity(fake_instance)
        self.assertTrue(self.adapter.has_active_entity("my_entity_id"))

    def test_get_active_entity(self):
        fake_entity = a(instance().with_metadata({}))
        self.db.entity.insert(fake_entity.as_dict())
        self.assertEqual(fake_entity, self.adapter.get_active_entity(fake_entity.entity_id))

    def test_get_active_entity_with_special_metadata_characters(self):
        fake_entity = a(instance().with_metadata({"a_metadata_not_sanitize": "not.sanitize",
                                                  "a_metadata^to_sanitize": "this.sanitize"}))

        self.db.entity.insert(fake_entity.as_dict())
        entity = self.adapter.get_active_entity(fake_entity.entity_id)

        expected_entity = a(instance()
                            .with_id(fake_entity.entity_id)
                            .with_project_id(fake_entity.project_id)
                            .with_metadata({"a_metadata_not_sanitize": "not.sanitize",
                                            "a_metadata.to_sanitize": "this.sanitize"}))

        self.assertEqual(entity, expected_entity)
        self.assert_entities_metadata_have_been_sanitize([entity])

    def test_get_active_entity_when_not_found(self):
        self.assertRaises(exception.EntityNotFoundException,
                          self.adapter.get_active_entity,
                          "will_not_found")

    def test_get_active_entity_with_unknown_type(self):
        fake_entity = a(instance())
        fake_entity.entity_type = "will_raise_exception"

        self.db.entity.insert(fake_entity.as_dict())
        self.assertRaises(exception.EntityTypeNotSupportedException,
                          self.adapter.get_active_entity,
                          fake_entity.entity_id)

    def test_count_entities(self):
        fake_active_entities = [
            a(volume()
              .with_id("id2")
              .with_start(2014, 1, 1, 1, 0, 0)
              .with_no_end()),
            a(instance()
              .with_id("id3")
              .with_start(2014, 1, 1, 8, 0, 0)
              .with_no_end()),
        ]
        fake_inactive_entities = [
            a(instance()
              .with_id("id1")
              .with_start(2014, 1, 1, 7, 0, 0)
              .with_end(2014, 1, 1, 8, 0, 0)),
            a(volume()
              .with_id("id2")
              .with_start(2014, 1, 1, 1, 0, 0)
              .with_end(2014, 1, 1, 8, 0, 0)),
        ]

        all_entities = fake_active_entities + fake_inactive_entities
        [self.db.entity.insert(fake_entity.as_dict()) for fake_entity in all_entities]

        self.assertEqual(4, self.adapter.count_entities())
        self.assertEqual(2, self.adapter.count_active_entities())
        self.assertEqual(1, self.adapter.count_entity_entries("id1"))
        self.assertEqual(2, self.adapter.count_entity_entries("id2"))

    def test_get_all_entities_by_id(self):
        fake_entity = a(instance().with_id("id1").with_start(2014, 1, 1, 8, 0, 0).with_no_end())
        self.db.entity.insert(fake_entity.as_dict())

        entries = self.adapter.get_all_entities_by_id(entity_id="id1")
        self.assertEqual(1, len(entries))
        self.assertEqual("id1", entries[0].entity_id)

        entries = self.adapter.get_all_entities_by_id(entity_id="id2")
        self.assertEqual(0, len(entries))

    def test_get_all_entities_by_project_and_type(self):
        fake_instances = [
            a(instance()
              .with_id("id1")
              .with_start(2014, 1, 1, 7, 0, 0)
              .with_end(2014, 1, 1, 8, 0, 0)
              .with_project_id("project_id")
              .with_metadata({})),
            a(instance()
              .with_id("id2")
              .with_start(2014, 1, 1, 1, 0, 0)
              .with_no_end()
              .with_project_id("project_id")
              .with_metadata({})),
            a(instance()
              .with_id("id3")
              .with_start(2014, 1, 1, 8, 0, 0)
              .with_no_end()
              .with_project_id("project_id")
              .with_metadata({})),
        ]

        fake_volumes = [
            a(volume()
              .with_id("id1")
              .with_start(2014, 1, 1, 7, 0, 0)
              .with_end(2014, 1, 1, 8, 0, 0)
              .with_project_id("project_id")),
            a(volume()
              .with_id("id2")
              .with_start(2014, 1, 1, 1, 0, 0)
              .with_no_end()
              .with_project_id("project_id")),
            a(volume()
              .with_id("id3")
              .with_start(2014, 1, 1, 8, 0, 0)
              .with_no_end()
              .with_project_id("project_id")),
        ]

        [self.db.entity.insert(fake_entity.as_dict()) for fake_entity in fake_instances + fake_volumes]

        entities = self.adapter.get_all_entities_by_project("project_id",
                                                            datetime(2014, 1, 1, 0, 0, 0, tzinfo=pytz.utc),
                                                            datetime(2014, 1, 1, 12, 0, 0, tzinfo=pytz.utc),
                                                            model.Instance.TYPE)
        self.assertEqual(3, len(entities))
        self.assertIn(fake_instances[0], entities)
        self.assertIn(fake_instances[1], entities)
        self.assertIn(fake_instances[2], entities)

    def test_get_all_entities_by_project_with_special_metadata_characters(self):
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

        [self.db.entity.insert(fake_entity.as_dict()) for fake_entity in fake_instances]

        entities = self.adapter.get_all_entities_by_project("project_id",
                                                            datetime(2014, 1, 1, 0, 0, 0, tzinfo=pytz.utc),
                                                            datetime(2014, 1, 1, 12, 0, 0, tzinfo=pytz.utc),
                                                            model.Instance.TYPE)

        self.assertEqual(2, len(entities))
        self.assertIn(expected_instances[0], entities)
        self.assertIn(expected_instances[1], entities)
        self.assert_entities_metadata_have_been_sanitize(entities)

    def test_get_all_entities_by_project(self):
        fake_entities_in_period = [
            a(instance()
                .with_id("in_the_period")
                .with_start(2014, 1, 1, 7, 0, 0)
                .with_end(2014, 1, 1, 8, 0, 0)
                .with_project_id("project_id")),
            a(instance()
              .with_id("running_has_started_before")
              .with_start(2014, 1, 1, 1, 0, 0)
              .with_no_end()
              .with_project_id("project_id")),
            a(instance()
              .with_id("running_has_started_during")
              .with_start(2014, 1, 1, 8, 0, 0)
              .with_no_end()
              .with_project_id("project_id")),
        ]
        fake_entities_out_period = [
            a(instance()
                .with_id("before_the_period")
                .with_start(2014, 1, 1, 0, 0, 0)
                .with_end(2014, 1, 1, 1, 0, 0)
                .with_project_id("project_id")),
            a(instance()
                .with_id("after_the_period")
                .with_start(2014, 1, 1, 10, 0, 0)
                .with_end(2014, 1, 1, 11, 0, 0)
                .with_project_id("project_id")),
            a(instance()
              .with_id("running_has_started_after")
              .with_start(2014, 1, 1, 10, 0, 0)
              .with_no_end()
              .with_project_id("project_id")),
        ]

        [self.db.entity.insert(fake_entity.as_dict())
         for fake_entity in fake_entities_in_period + fake_entities_out_period]

        entities = self.adapter.get_all_entities_by_project("project_id",
                                                            datetime(2014, 1, 1, 6, 0, 0, tzinfo=pytz.utc),
                                                            datetime(2014, 1, 1, 9, 0, 0, tzinfo=pytz.utc))
        self.assertEqual(3, len(entities))
        entity_ids = [entity.entity_id for entity in entities]
        self.assertIn(fake_entities_in_period[0].entity_id, entity_ids)
        self.assertIn(fake_entities_in_period[1].entity_id, entity_ids)
        self.assertIn(fake_entities_in_period[2].entity_id, entity_ids)

    def test_get_all_entities_by_id_and_date(self):
        start = datetime(2016, 3, 1, 0, 0, 0, 0, pytz.utc)
        end = datetime(2016, 3, 3, 0, 0, 0, 0, pytz.utc)
        instances = [
            a(instance()
              .with_name("instance with end date")
              .with_id("id1")
              .with_start(2016, 3, 1, 0, 0, 0)
              .with_end(2016, 3, 2, 0, 0, 0)),
            a(instance()
              .with_name("instance with no end date")
              .with_id("id1")
              .with_start(2016, 3, 2, 0, 0, 0)
              .with_no_end()),
        ]

        [self.db.entity.insert(fake_instance.as_dict()) for fake_instance in instances]
        entities = self.adapter.get_all_entities_by_id_and_date("id1", start, end)

        self.assertEqual(1, len(entities))
        self.assertEqual("instance with end date", entities[0].name)

    def test_close_active_entity(self):
        fake_entity = a(instance())
        end_date = datetime(2015, 10, 21, 16, 29, 0)

        self.db.entity.insert(fake_entity.as_dict())
        self.adapter.close_active_entity(fake_entity.entity_id, end_date)

        self.assertEqual(self.db.entity.find_one({"entity_id": fake_entity.entity_id})["end"], end_date)

    def test_update_closed_entity(self):
        fake_entity = a(instance().with_end(2016, 3, 2, 0, 0, 0))

        self.db.entity.insert(fake_entity.as_dict())
        fake_entity.flavor = "my_new_flavor"
        self.adapter.update_closed_entity(fake_entity, data={"flavor": fake_entity.flavor})

        db_entity = self.db.entity.find_one({"entity_id": fake_entity.entity_id})
        self.assertEqual(db_entity['flavor'], fake_entity.flavor)
        self.assertEqual(db_entity['end'], fake_entity.end)

    def test_update_active_entity(self):
        fake_entity = a(instance())
        fake_entity.image_meta['distro'] = "Centos"

        self.db.entity.insert(fake_entity.as_dict())
        fake_entity.image_meta['distro'] = "Windows"

        self.adapter.update_active_entity(fake_entity)

        self.assertEqual(self.db.entity.find_one({"entity_id": fake_entity.entity_id})["os"]["distro"],
                         fake_entity.image_meta['distro'])
        self.assertEqual(self.db.entity.find_one({"entity_id": fake_entity.entity_id})["image_meta"]["distro"],
                         fake_entity.image_meta['distro'])

    def test_delete_active_entity(self):
        fake_entity = a(volume())

        self.db.entity.insert(fake_entity.as_dict())
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
        self.db.volume_type.insert(fake_volume_type.as_dict())
        self.assertEqual(self.adapter.get_volume_type(fake_volume_type.volume_type_id), fake_volume_type)

    def test_get_volume_type_that_does_not_exists(self):
        fake_volume_type = a(volume_type())

        self.assertRaises(exception.VolumeTypeNotFoundException,
                          self.adapter.get_volume_type,
                          fake_volume_type.volume_type_id)

    def test_delete_volume_type(self):
        fake_volume_type = a(volume_type())
        self.db.volume_type.insert(fake_volume_type.as_dict())
        self.assertEqual(1, self.db.volume_type.count())
        self.adapter.delete_volume_type(fake_volume_type.volume_type_id)
        self.assertEqual(0, self.db.volume_type.count())

    def test_delete_volume_type_not_in_database(self):
        self.assertRaises(exception.VolumeTypeNotFoundException,
                          self.adapter.delete_volume_type,
                          "not_in_database_id")

    def test_delete_all_volume_types_is_not_permitted(self):
        self.assertRaises(exception.AlmanachException,
                          self.adapter.delete_volume_type,
                          None)

    def test_list_volume_types(self):
        fake_volume_types = [a(volume_type()), a(volume_type())]

        for fake_volume_type in fake_volume_types:
            self.db.volume_type.insert(fake_volume_type.as_dict())

        self.assertEqual(len(self.adapter.list_volume_types()), 2)

    def assert_mongo_collection_contains(self, collection, obj):
        self.assertTrue(obj.as_dict() in self.db[collection].find(fields={"_id": 0}),
                        "The collection '{}' does not contains the object of type '{}'".format(collection, type(obj)))

    def assert_entities_metadata_have_been_sanitize(self, entities):
        for entity in entities:
            for key in entity.metadata:
                self.assertTrue(key.find("^") == -1,
                                "The metadata key {} contains caret".format(key))
