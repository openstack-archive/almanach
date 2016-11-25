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

from hamcrest import assert_that
from hamcrest import calling
from hamcrest import is_
from hamcrest import raises

from almanach.core import exception
from almanach.validators.instance_validator import InstanceValidator


class InstanceValidatorTests(unittest.TestCase):
    def test_validate_update_with_invalid_attribute(self):
        instance_validator = InstanceValidator()
        payload = {"invalid attribute": ".."}
        assert_that(calling(instance_validator.validate_update).with_args(payload),
                    raises(exception.InvalidAttributeException))

    def test_validate_update_with_valid_name_attribute(self):
        instance_validator = InstanceValidator()
        payload = {"name": u"instance name"}

        assert_that(instance_validator.validate_update(payload), is_(payload))

    def test_validate_update_with_invalid_name_attribute(self):
        instance_validator = InstanceValidator()
        payload = {"name": 123}

        assert_that(calling(instance_validator.validate_update).with_args(payload),
                    raises(exception.InvalidAttributeException))

    def test_validate_update_with_valid_flavor_attribute(self):
        instance_validator = InstanceValidator()
        payload = {"flavor": u"flavor"}

        assert_that(instance_validator.validate_update(payload), is_(payload))

    def test_validate_update_with_invalid_flavor_attribute(self):
        instance_validator = InstanceValidator()
        payload = {"flavor": 123}

        assert_that(calling(instance_validator.validate_update).with_args(payload),
                    raises(exception.InvalidAttributeException))

    def test_validate_update_with_valid_start_date(self):
        instance_validator = InstanceValidator()
        payload = {"start_date": "2015-10-21T16:25:00.000000Z"}

        assert_that(instance_validator.validate_update(payload),
                    is_(payload))

    def test_validate_update_with_invalid_start_date(self):
        instance_validator = InstanceValidator()
        payload = {"start_date": "2015-10-21"}

        assert_that(calling(instance_validator.validate_update).with_args(payload),
                    raises(exception.InvalidAttributeException))

    def test_validate_update_with_valid_end_date(self):
        instance_validator = InstanceValidator()
        payload = {"end_date": "2015-10-21T16:25:00.000000Z"}

        assert_that(instance_validator.validate_update(payload),
                    is_(payload))

    def test_validate_update_with_invalid_end_date(self):
        instance_validator = InstanceValidator()
        payload = {"end_date": "2016"}

        assert_that(calling(instance_validator.validate_update).with_args(payload),
                    raises(exception.InvalidAttributeException))

    def test_validate_update_with_valid_os_attribute(self):
        instance_validator = InstanceValidator()
        payload = {
            "os": {
                "distro": u"centos",
                "version": u"7",
                "os_type": u"linux",
            }
        }

        assert_that(instance_validator.validate_update(payload), is_(payload))

    def test_validate_update_with_invalid_os_attribute(self):
        instance_validator = InstanceValidator()
        payload = {
            "os": {
                "distro": u"centos",
                "os_type": u"linux",
            }
        }

        assert_that(calling(instance_validator.validate_update).with_args(payload),
                    raises(exception.InvalidAttributeException))

    def test_validate_update_with_valid_metadata_attribute(self):
        instance_validator = InstanceValidator()
        payload = {
            "metadata": {
                "key": "value"
            }
        }

        assert_that(instance_validator.validate_update(payload), is_(payload))

        instance_validator = InstanceValidator()
        payload = {
            "metadata": {}
        }

        assert_that(instance_validator.validate_update(payload), is_(payload))

    def test_validate_update_with_invalid_metadata_attribute(self):
        instance_validator = InstanceValidator()
        payload = {
            "metadata": "foobar"
        }

        assert_that(calling(instance_validator.validate_update).with_args(payload),
                    raises(exception.InvalidAttributeException))
