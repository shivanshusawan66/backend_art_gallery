class InternalServerException(Exception):
    """Raise when internal server error"""

    def __init__(self, message: str = None):
        self.message = message


class MongoDocumentNotFoundException(Exception):
    """Raise when no matching document is found for a given query"""

    def __init__(self, message: str = None):
        self.message = message


class MongoConnectionFailException(Exception):
    """Raise when the Mongo ping fails"""

    def __init__(self, message: str = None):
        self.message = message


class DataTypeNotHandledException(Exception):
    """Raise when the datatype provided is not handled"""

    def __init__(self, message: str = None):
        self.message = message
