from voluptuous import Schema, MultipleInvalid, Datetime, Required

from almanach.common.exceptions.validation_exception import InvalidAttributeException


class InstanceValidator(object):
    def __init__(self):
        self.schema = Schema({
            'name': unicode,
            'flavor': unicode,
            'os': {
                Required('distro'): unicode,
                Required('version'): unicode,
                Required('os_type'): unicode,
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
