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

import logging

import pymongo
from pymongo import errors

from almanach import config
from almanach.core import exception
from almanach.core import model
from almanach.core.model import build_entity_from_dict


def database(function):
    def _connection(self, *args, **kwargs):
        try:
            if not self.db:
                connection = pymongo.MongoClient(config.mongodb_url(), tz_aware=True)
                self.db = connection[config.mongodb_database()]
                ensureindex(self.db)
            return function(self, *args, **kwargs)
        except KeyError as e:
            raise e
        except exception.VolumeTypeNotFoundException as e:
            raise e
        except NotImplementedError as e:
            raise e
        except errors.ConfigurationError as e:
            logging.exception("DB Connection, make sure username and password doesn't contain the following :+&/ "
                              "character")
            raise e
        except Exception as e:
            logging.exception(e)
            raise e

    return _connection


def ensureindex(db):
    db.entity.ensure_index(
        [(index, pymongo.ASCENDING)
         for index in config.mongodb_indexes()])


class DatabaseAdapter(object):
    def __init__(self):
        self.db = None

    @database
    def get_active_entity(self, entity_id):
        entity = self._get_one_entity_from_db({"entity_id": entity_id, "end": None})
        if not entity:
            raise KeyError("Unable to find entity id %s" % entity_id)
        return build_entity_from_dict(entity)

    @database
    def count_entities(self):
        return self.db.entity.count()

    @database
    def count_active_entities(self):
        return self.db.entity.find({"end": None}).count()

    @database
    def count_entity_entries(self, entity_id):
        return self.db.entity.find({"entity_id": entity_id}).count()

    @database
    def has_active_entity(self, entity_id):
        return self.db.entity.find({"entity_id": entity_id, "end": None}).count() == 1

    @database
    def list_entities(self, project_id, start, end, entity_type=None):
        args = {"project_id": project_id, "start": {"$lte": end}, "$or": [{"end": None}, {"end": {"$gte": start}}]}
        if entity_type:
            args["entity_type"] = entity_type
        entities = self._get_entities_from_db(args)
        return [build_entity_from_dict(entity) for entity in entities]

    @database
    def get_all_entities_by_id(self, entity_id):
        entities = self.db.entity.find({"entity_id": entity_id}, {"_id": 0})
        return [build_entity_from_dict(entity) for entity in entities]

    @database
    def list_entities_by_id(self, entity_id, start, end):
        entities = self.db.entity.find({"entity_id": entity_id,
                                        "start": {"$gte": start},
                                        "$and": [
                                            {"end": {"$ne": None}},
                                            {"end": {"$lte": end}}
                                        ]
                                        }, {"_id": 0})
        return [build_entity_from_dict(entity) for entity in entities]

    @database
    def update_closed_entity(self, entity, data):
        self.db.entity.update({"entity_id": entity.entity_id, "start": entity.start, "end": entity.end},
                              {"$set": data})

    @database
    def insert_entity(self, entity):
        self._insert_entity(entity.as_dict())

    @database
    def insert_volume_type(self, volume_type):
        self.db.volume_type.insert(volume_type.__dict__)

    @database
    def get_volume_type(self, volume_type_id):
        volume_type = self.db.volume_type.find_one({"volume_type_id": volume_type_id})
        if not volume_type:
            logging.error("Trying to get a volume type not in the database.")
            raise exception.VolumeTypeNotFoundException(volume_type_id=volume_type_id)

        return model.VolumeType(volume_type_id=volume_type["volume_type_id"],
                                volume_type_name=volume_type["volume_type_name"])

    @database
    def delete_volume_type(self, volume_type_id):
        if volume_type_id is None:
            error = "Trying to delete all volume types which is not permitted."
            logging.error(error)
            raise exception.AlmanachException(error)
        returned_value = self.db.volume_type.remove({"volume_type_id": volume_type_id})
        if returned_value['n'] == 1:
            logging.info("Deleted volume type with id '%s' successfully." % volume_type_id)
        else:
            error = "Volume type with id '%s' doesn't exist in the database." % volume_type_id
            logging.error(error)
            raise exception.AlmanachException(error)

    @database
    def list_volume_types(self):
        volume_types = self.db.volume_type.find()
        return [model.VolumeType(volume_type_id=volume_type["volume_type_id"],
                                 volume_type_name=volume_type["volume_type_name"]) for volume_type in volume_types]

    @database
    def close_active_entity(self, entity_id, end):
        self.db.entity.update({"entity_id": entity_id, "end": None}, {"$set": {"end": end, "last_event": end}})

    @database
    def update_active_entity(self, entity):
        self.db.entity.update({"entity_id": entity.entity_id, "end": None}, {"$set": entity.as_dict()})

    @database
    def delete_active_entity(self, entity_id):
        self.db.entity.remove({"entity_id": entity_id, "end": None})

    def _insert_entity(self, entity):
        self.db.entity.insert(entity)

    def _get_entities_from_db(self, args):
        return list(self.db.entity.find(args, {"_id": 0}))

    def _get_one_entity_from_db(self, args):
        return self.db.entity.find_one(args, {"_id": 0})
