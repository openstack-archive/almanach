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
from dateutil import parser as date_parser
import six

import pytz

from almanach.core import exception


@six.add_metaclass(abc.ABCMeta)
class BaseController(object):

    def _validate_and_parse_date(self, date):
        try:
            date = date_parser.parse(date)
            return self._localize_date(date)
        except (TypeError, ValueError):
            raise exception.DateFormatException()

    @staticmethod
    def _localize_date(date):
        try:
            return pytz.utc.localize(date)
        except ValueError:
            return date

    def _fresher_entity_exists(self, entity_id, date):
        try:
            entity = self.database_adapter.get_active_entity(entity_id)
            if entity and entity.last_event > date:
                return True
        except exception.EntityNotFoundException:
            pass
        except exception.EntityTypeNotSupportedException:
            pass
        return False

    def _transform_attribute_to_match_entity_attribute(self, **kwargs):
        entity = {}
        for attribute, key in dict(start="start_date", end="end_date").items():
            if kwargs.get(key):
                entity[attribute] = self._validate_and_parse_date(kwargs.get(key))

        for attribute in ["name", "flavor", "os", "metadata"]:
            if kwargs.get(attribute):
                entity[attribute] = kwargs.get(attribute)
        return entity
