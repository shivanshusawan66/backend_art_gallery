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


class PasswordNotValidException(Exception):
    """Raise when the provided password is not valid."""

    def __init__(self, message: str = "The provided password is not valid."):
        self.message = message
        super().__init__(self.message)


class MalformedJWTRequestException(Exception):
    """Raise when the JWT request is malformed."""

    def __init__(self, message: str = "The JWT request is malformed."):
        self.message = message
        super().__init__(self.message)

def generate_detailed_errors(errors):
    detailed_errors = []
    for error in errors:

        location = error.get("loc", [])

        field_name = str(location[-1]) if location else "Unknown field"

        error_type_map = {
            "missing": "Required field missing",
            "type_error": "Invalid type",
            "value_error": "Invalid value",
        }

        error_type = error.get("type", "unknown")
        base_message = error_type_map.get(error_type, "Validation error")

        detailed_errors.append(
            {
                "type": error_type,
                "location": location,
                "field": field_name,
                "message": f"{base_message} for {field_name.replace('_', ' ').title()}",
                "input": error.get("input"),
            }
        )

    return detailed_errors

class AssignWeightException(Exception):
    """Raise if some error occured while assigning weights """

    def __init__(self, message: str = "An error occurred while assigning weights."):
        self.message = message
        super().__init__(self.message)