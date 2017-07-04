# Imported from flask-rest-jsonapi
# https://github.com/miLibris/flask-rest-jsonapi
import http.client

from .errors import Error, Source


class JsonApiException(Exception):
    status = http.client.INTERNAL_SERVER_ERROR
    title = "Unknown error"

    def __init__(self, errors=None):
        """Initialize a jsonapi exception.
        It is different from an ordinary exception as it can host
        multiple error conditions, and they can be serialized to a
        JSONAPI representation for appropriate output.

        Parameters
        ----------
        errors: List or None
            A list of Error objects.
            if None, a single error will be generated, using the class
            status and title
        """
        if errors is None:
            errors = [Error(title=self.title,
                            status=self.status)]

        self.errors = errors

    def to_jsonapi(self):
        """Converts the exception in a JSONAPI representation of
        the contained information."""
        return [
            error.to_jsonapi()
            for error in self.errors
        ]

    @classmethod
    def from_message(cls, message):
        """Returns an instance of the exception class,
        specifying the message"""
        return cls(errors=[Error(
            title=cls.title,
            status=cls.status,
            detail=message
        )])

    @classmethod
    def from_pointer_and_message(cls, pointer, message):
        """Returns an instance of the exception class,
        specifying the pointer and the message"""
        return cls(errors=[Error(
            source=Source(pointer=pointer),
            title=cls.title,
            status=cls.status,
            detail=message
        )])


class BadRequest(JsonApiException):
    status = http.client.BAD_REQUEST
    title = "Bad request"


class ValidationError(JsonApiException):
    status = http.client.UNPROCESSABLE_ENTITY
    title = "Validation error"


class InvalidFields(BadRequest):
    title = "Invalid fields querystring parameter"

    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title=self.title,
                            source=Source(parameter="fields"),
                            status=self.status)]

        super().__init__(errors)


class InvalidInclude(BadRequest):
    title = "Invalid include querystring parameter"

    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title=self.title,
                            source=Source(parameter="include"),
                            status=self.status)]

        super().__init__(errors)


class InvalidFilters(BadRequest):
    title = "Invalid filters querystring parameter"

    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title=self.title,
                            source=Source(parameter="filters"),
                            status=self.status)]

        super().__init__(errors)


class InvalidSort(BadRequest):
    title = "Invalid sort querystring parameter"

    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title=self.title,
                            source=Source(parameter="sort"),
                            status=self.status)]

        super().__init__(errors)


class ObjectNotFound(JsonApiException):
    status = http.client.NOT_FOUND
    title = "Object not found"


class RelatedObjectNotFound(ObjectNotFound):
    title = "Related object not found"


class RelationNotFound(ObjectNotFound):
    title = "Relation object not found"


class ObjectAlreadyPresent(JsonApiException):
    status = http.client.CONFLICT
    title = "Object already present"


class InvalidType(JsonApiException):
    status = http.client.CONFLICT
    title = "Invalid type"


class InvalidIdentifier(JsonApiException):
    status = http.client.CONFLICT
    title = "Invalid identifier"


class Unable(JsonApiException):
    status = http.client.INTERNAL_SERVER_ERROR
    title = "Unable to perform operation"
