# Copyright 2017 Internap.
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
from dateutil import parser
import pytz

from almanach.core import exception


class DateHelper(object):

    @staticmethod
    def parse(value):
        try:
            dt = value if isinstance(value, datetime) else parser.parse(value)
            return DateHelper._normalize_timezone(dt)
        except (TypeError, ValueError):
            raise exception.DateFormatException()

    @staticmethod
    def is_within_range(d1, d2, delta):
        diff = (d2 - d1).total_seconds()
        return abs(diff) < delta

    @staticmethod
    def _normalize_timezone(dt):
        try:
            return dt.astimezone(pytz.utc)
        except ValueError:
            return dt.replace(tzinfo=pytz.utc)
