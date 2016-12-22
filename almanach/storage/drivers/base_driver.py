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


@six.add_metaclass(abc.ABCMeta)
class BaseDriver(object):

    def __init__(self, config):
        self.config = config

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def get_active_entity(self, entity_id):
        pass

    @abc.abstractmethod
    def count_entities(self):
        pass

    @abc.abstractmethod
    def count_active_entities(self):
        pass

    @abc.abstractmethod
    def count_entity_entries(self, entity_id):
        pass

    @abc.abstractmethod
    def has_active_entity(self, entity_id):
        pass

    @abc.abstractmethod
    def get_all_entities_by_project(self, project_id, start, end, entity_type=None):
        pass

    @abc.abstractmethod
    def get_all_entities_by_id(self, entity_id):
        pass

    @abc.abstractmethod
    def get_all_entities_by_id_and_date(self, entity_id, start, end):
        pass

    @abc.abstractmethod
    def update_closed_entity(self, entity, data):
        pass

    @abc.abstractmethod
    def insert_entity(self, entity):
        pass

    @abc.abstractmethod
    def close_active_entity(self, entity_id, end):
        pass

    @abc.abstractmethod
    def update_active_entity(self, entity):
        pass

    @abc.abstractmethod
    def delete_active_entity(self, entity_id):
        pass

    @abc.abstractmethod
    def insert_volume_type(self, volume_type):
        pass

    @abc.abstractmethod
    def get_volume_type(self, volume_type_id):
        pass

    @abc.abstractmethod
    def delete_volume_type(self, volume_type_id):
        pass

    @abc.abstractmethod
    def list_volume_types(self):
        pass
