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
import pytz

from almanach.core.helpers import date_helper

from almanach.tests.unit import base


class TestDateHelper(base.BaseTestCase):

    def setUp(self):
        super(TestDateHelper, self).setUp()
        self.helper = date_helper.DateHelper()

    def test_parser_with_datetime_object(self):
        original_datetime = datetime.now(tz=pytz.utc)
        d = self.helper.parse(original_datetime)
        self.assertEqual(original_datetime, d)

    def test_parser_created_at_string(self):
        d = self.helper.parse('2017-02-15 05:22:57+00:00')
        self.assertIsInstance(d, datetime)
        self.assertEqual(d.day, 15)
        self.assertEqual(d.month, 2)
        self.assertEqual(d.year, 2017)
        self.assertEqual(d.hour, 5)
        self.assertEqual(d.minute, 22)
        self.assertEqual(d.second, 57)
        self.assertEqual(d.tzinfo, pytz.utc)

    def test_parser_deleted_at_string(self):
        d = self.helper.parse('2017-02-05T11:34:36.000000')
        self.assertIsInstance(d, datetime)
        self.assertEqual(d.day, 5)
        self.assertEqual(d.month, 2)
        self.assertEqual(d.year, 2017)
        self.assertEqual(d.hour, 11)
        self.assertEqual(d.minute, 34)
        self.assertEqual(d.second, 36)
        self.assertEqual(d.tzinfo, pytz.utc)

    def test_is_whithin_range(self):
        d1 = self.helper.parse('2017-02-15 05:22:57+00:00')
        d2 = self.helper.parse('2017-02-15T05:30:04.000000')
        self.assertFalse(self.helper.is_within_range(d1, d2, 30))
        self.assertTrue(self.helper.is_within_range(d1, d2, 600))

        d2 = self.helper.parse('2017-02-15 05:22:57+00:00')
        d1 = self.helper.parse('2017-02-15T05:30:04.000000')
        self.assertFalse(self.helper.is_within_range(d1, d2, 30))
        self.assertTrue(self.helper.is_within_range(d1, d2, 600))
