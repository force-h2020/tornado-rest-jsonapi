import http.client
import json

from marshmallow import ValidationError
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from tornado import web, gen, escape
from tornado.log import app_log
from . import exceptions
from .errors import jsonapi_errors, errors_from_jsonapi_errors
from .pagination import pagination_links
from .schema import compute_schema
from .querystring import QueryStringManager as QSManager

_CONTENT_TYPE_JSONAPI = 'application/vnd.api+json'


class Resource(web.RequestHandler):
    data_layer = None
    schema = None

    def initialize(self, registry, base_urlpath):
        """Initialization method for when the class is instantiated."""
        self._registry = registry
        self._base_urlpath = base_urlpath

    @gen.coroutine
    def prepare(self):
        """Runs before any specific handler. """
        authenticator = self.registry.authenticator
        self.current_user = yield authenticator.authenticate(self)

    @property
    def registry(self):
        """Returns the class vs Resource registry"""
        return self._registry

    @property
    def base_urlpath(self):
        """Returns the Base urlpath as from initial setup"""
        return self._base_urlpath

    @property
    def log(self):
        return app_log

    def get_data_layer_instance(self):
        data_layer_cls = self.data_layer["class"]
        data_layer_kwargs = dict(self.data_layer)
        data_layer_kwargs.pop("class", None)
        data_layer_kwargs["application"] = self.application
        data_layer_kwargs["current_user"] = self.current_user

        return data_layer_cls(data_layer_kwargs)

    def write_error(self, status_code, **kwargs):
        """Provides appropriate payload to the response in case of error.
        """
        exc_info = kwargs.get("exc_info")

        if exc_info is None:
            self.clear_header('Content-Type')
            self.finish()

        exc = exc_info[1]

        if isinstance(exc, exceptions.JsonApiException):
            self.set_header('Content-Type', _CONTENT_TYPE_JSONAPI)
            self.set_status(exc.status)
            self.finish(escape.json_encode(jsonapi_errors(exc)))
        elif isinstance(exc, json.decoder.JSONDecodeError):
            self.clear_header('Content-Type')
            self.set_status(http.client.BAD_REQUEST)
            self.finish()
        else:
            # For non-payloaded http errors or any other exception
            # we don't want to return anything as payload.
            # The error code is enough.
            self.set_status(status_code)
            self.clear_header('Content-Type')
            self.finish()

    def _send_to_client(self, entity):
        """Convenience method to send a given entity to a client.
        Serializes it and puts the right headers.
        If entity is None, sets no content http response."""

        if entity is None:
            self.clear_header('Content-Type')
            self.set_status(http.client.NO_CONTENT)
            return

        self.set_header("Content-Type", _CONTENT_TYPE_JSONAPI)
        response = entity
        if isinstance(entity, dict):
            response = {}
            response.update(entity)
            response["jsonapi"] = {
                "version": "1.0"
            }

        self.set_status(http.client.OK)
        self.write(escape.json_encode(response))
        self.flush()

    def _send_created_to_client(self, location):
        """Sends a created message to the client for a given resource

        """
        self.set_status(int(http.client.CREATED))
        self.set_header("Location", location)
        self.clear_header('Content-Type')
        self.flush()


class ResourceList(Resource):
    """Handler for URLs without an identifier.
    """
    @gen.coroutine
    def get(self, *args, **view_kwargs):
        data_layer = self.get_data_layer_instance()
        qs = QSManager(self.request.arguments, self.schema)

        total_num, items = yield data_layer.get_collection(qs, view_kwargs)

        schema = compute_schema(self.schema,
                                {"many": True},
                                qs,
                                qs.include)
        result = schema.dump(items).data
        result["links"] = pagination_links(total_num,
                                           qs,
                                           self.request.full_url())
        self._send_to_client(result)

    @gen.coroutine
    def post(self, *args, **view_kwargs):
        data_layer = self.get_data_layer_instance()
        qs = QSManager(self.request.arguments, self.schema)

        json_data = escape.json_decode(self.request.body)

        schema = compute_schema(self.schema,
                                {},
                                qs,
                                qs.include)
        try:
            data, errors = schema.load(json_data)
        except IncorrectTypeError as e:
            errors = e.messages
            for error in errors['errors']:
                error['status'] = '409'
                error['title'] = "Incorrect type"
            raise exceptions.InvalidType(
                errors_from_jsonapi_errors(errors))
        except ValidationError as e:
            errors = e.messages
            for message in errors['errors']:
                message['status'] = '422'
                message['title'] = "Validation error"

            raise exceptions.ValidationError(
                errors_from_jsonapi_errors(errors))

        if errors:
            raise exceptions.BadRequest(errors_from_jsonapi_errors(errors))

        obj = yield data_layer.create_object(data, view_kwargs)
        result = schema.dump(obj).data

        location = result['data']['links']['self']
        self._send_created_to_client(location)


class ResourceDetails(Resource):
    """Handler for URLs addressing a resource.
    """
    @gen.coroutine
    def get(self, *args, **view_kwargs):
        """Retrieves the resource representation."""
        data_layer = self.get_data_layer_instance()
        qs = QSManager(self.request.arguments, self.schema)
        schema = compute_schema(self.schema,
                                {},
                                qs,
                                qs.include)

        obj = yield data_layer.get_object(view_kwargs)

        result = schema.dump(obj).data

        self._send_to_client(result)

    @gen.coroutine
    def patch(self, *args, **view_kwargs):
        data_layer = self.get_data_layer_instance()
        qs = QSManager(self.request.arguments, self.schema)

        json_data = escape.json_decode(self.request.body)

        schema = compute_schema(self.schema,
                                {"partial": True},
                                qs,
                                qs.include)

        try:
            data, errors = schema.load(json_data)
        except IncorrectTypeError as e:
            errors = e.messages
            for error in errors['errors']:
                error['status'] = '409'
                error['title'] = "Incorrect type"
            raise exceptions.InvalidType(errors_from_jsonapi_errors(errors))
        except ValidationError as e:
            errors = e.messages
            for message in errors['errors']:
                message['status'] = '422'
                message['title'] = "Validation error"
            raise exceptions.ValidationError(
                errors_from_jsonapi_errors(errors))
        if errors:
            raise exceptions.BadRequest(errors_from_jsonapi_errors(errors))

        if 'id' not in json_data['data']:
            raise exceptions.InvalidIdentifier()

        if str(json_data['data']['id']) != str(
                view_kwargs[self.data_layer.get('url_field', 'id')]):
            raise exceptions.InvalidIdentifier()

        obj = yield data_layer.get_object(view_kwargs)
        updated_obj = yield data_layer.update_object(obj, data, view_kwargs)

        result = schema.dump(updated_obj).data

        self._send_to_client(result)

    @gen.coroutine
    def post(self, *args, **view_kwargs):
        """This operation is not possible in REST, and results
        in either Conflict or NotFound, depending on the
        presence of a resource at the given URL"""
        data_layer = self.get_data_layer_instance()

        try:
            yield data_layer.get_object(view_kwargs)
        except exceptions.ObjectNotFound:
            raise
        else:
            raise exceptions.ObjectAlreadyPresent()

    @gen.coroutine
    def delete(self, *args, **view_kwargs):
        """Deletes the resource."""

        data_layer = self.get_data_layer_instance()

        obj = yield data_layer.get_object(view_kwargs)
        yield data_layer.delete_object(obj, view_kwargs)

        result = {'meta': {'message': 'Object successfully deleted'}}
        self._send_to_client(result)
