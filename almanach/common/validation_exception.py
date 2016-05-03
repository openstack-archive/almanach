class InvalidAttributeException(Exception):
    def __init__(self, errors):
        self.errors = errors

    def get_error_message(self):
        messages = {}
        for error in self.errors:
            messages[error.path[0]] = error.msg

        return messages
