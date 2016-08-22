import six
from voluptuous import Schema, MultipleInvalid, Datetime, Required

from almanach.common.exceptions.validation_exception import InvalidAttributeException


class InstanceValidator(object):
    def __init__(self):
        self.schema = Schema({
            'name': six.text_type,
            'flavor': six.text_type,
            'os': {
                Required('distro'): six.text_type,
                Required('version'): six.text_type,
                Required('os_type'): six.text_type,
            },
            'metadata': dict,
            'start_date': Datetime(),
            'end_date': Datetime(),
        })

    def validate_update(self, payload):
        try:
            return self.schema(payload)
        except MultipleInvalid as e:
            raise InvalidAttributeException(e.errors)
