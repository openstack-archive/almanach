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

from almanach.core import exception
from almanach.storage.drivers import mongodb_driver
from almanach.storage import storage_driver

from almanach.tests.unit import base


class TestStorageDriver(base.BaseTestCase):

    def setUp(self):
        super(TestStorageDriver, self).setUp()
        self.storage_driver = storage_driver.StorageDriver(self.config)

    def test_get_default_database_adapter(self):
        self.assertIsInstance(self.storage_driver.get_database_driver(), mongodb_driver.MongoDbDriver)

    def test_get_unknown_database_adapter(self):
        self.config_fixture.config(driver='foobar', group='database')
        self.assertRaises(exception.DatabaseDriverNotSupportedException, self.storage_driver.get_database_driver)
