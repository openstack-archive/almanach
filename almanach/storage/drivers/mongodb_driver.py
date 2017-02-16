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

import pymongo

from almanach.core import exception
from almanach.core import model
from almanach.core.model import get_entity_from_dict
from almanach.storage.drivers import base_driver


class MongoDbDriver(base_driver.BaseDriver):

    def __init__(self, config, db=None):
        super(MongoDbDriver, self).__init__(config)
        self.db = db

    def connect(self):
        connection = pymongo.MongoClient(self.config.database.connection_url, tz_aware=True)
        connection_options = pymongo.uri_parser.parse_uri(self.config.database.connection_url)
        self.db = connection[connection_options['database']]

    def count_entities(self):
        return self.db.entity.count()

    def count_active_entities(self):
        return self.db.entity.find({"end": None}).count()

    def count_entity_entries(self, entity_id):
        return self.db.entity.find({"entity_id": entity_id}).count()

    def has_active_entity(self, entity_id):
        return self.db.entity.find({"entity_id": entity_id, "end": None}).count() == 1

    def get_active_entity(self, entity_id):
        entity = self.db.entity.find_one({"entity_id": entity_id, "end": None}, {"_id": 0})
        if not entity:
            raise exception.EntityNotFoundException("Entity {} not found".format(entity_id))
        return get_entity_from_dict(entity)

    def get_all_entities_by_project(self, project_id, start, end, entity_type=None):
        args = {
            "project_id": project_id,
            "start": {
                "$lte": end
            },
            "$or": [{"end": None}, {"end": {"$gte": start}}]
        }

        if entity_type:
            args["entity_type"] = entity_type

        entities = list(self.db.entity.find(args, {"_id": 0}))
        return [get_entity_from_dict(entity) for entity in entities]

    def get_all_entities_by_id(self, entity_id):
        entities = self.db.entity.find({"entity_id": entity_id}, {"_id": 0})
        return [get_entity_from_dict(entity) for entity in entities]

    def get_all_entities_by_id_and_date(self, entity_id, start, end):
        entities = self.db.entity.find({
            "entity_id": entity_id,
            "start": {"$gte": start},
            "$and": [
                {"end": {"$ne": None}},
                {"end": {"$lte": end}}
            ]
        }, {"_id": 0})
        return [get_entity_from_dict(entity) for entity in entities]

    def close_active_entity(self, entity_id, end):
        self.db.entity.update({"entity_id": entity_id, "end": None}, {"$set": {"end": end, "last_event": end}})

    def insert_entity(self, entity):
        self.db.entity.insert(entity.as_dict())

    def update_active_entity(self, entity):
        self.db.entity.update({"entity_id": entity.entity_id, "end": None}, {"$set": entity.as_dict()})

    def update_closed_entity(self, entity, data):
        self.db.entity.update({"entity_id": entity.entity_id, "start": entity.start, "end": entity.end},
                              {"$set": data})

    def delete_active_entity(self, entity_id):
        self.db.entity.remove({"entity_id": entity_id, "end": None})

    def insert_volume_type(self, volume_type):
        self.db.volume_type.insert(volume_type.__dict__)

    def list_volume_types(self):
        volume_types = self.db.volume_type.find()
        return [model.VolumeType(volume_type_id=volume_type["volume_type_id"],
                                 volume_type_name=volume_type["volume_type_name"]) for volume_type in volume_types]

    def get_volume_type(self, volume_type_id):
        volume_type = self.db.volume_type.find_one({"volume_type_id": volume_type_id})
        if not volume_type:
            raise exception.VolumeTypeNotFoundException(volume_type_id=volume_type_id)
        return model.VolumeType.from_dict(volume_type)

    def delete_volume_type(self, volume_type_id):
        if volume_type_id is None:
            raise exception.AlmanachException("Trying to delete all volume types which is not permitted.")
        returned_value = self.db.volume_type.remove({"volume_type_id": volume_type_id})
        if returned_value['n'] != 1:
            raise exception.VolumeTypeNotFoundException(volume_type_id)
