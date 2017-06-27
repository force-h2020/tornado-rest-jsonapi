import http.client
import json

from marshmallow import ValidationError
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from tornado import web, gen, escape
from tornado.log import app_log
from tornado.web import HTTPError
from . import exceptions
from .errors import jsonapi_errors, errors_from_jsonapi_errors
from .pagination import pagination_links
from .schema import compute_schema
from .utils import with_end_slash, url_path_join
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

    def get_data_layer(self):
        data_layer_cls = self.data_layer["class"]
        data_layer_kwargs = dict(self.data_layer)
        data_layer_kwargs.pop("class", None)
        data_layer_kwargs["application"] = self.application
        data_layer_kwargs["current_user"] = self.current_user

        return data_layer_cls(**data_layer_kwargs)

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

    def _send_created_to_client(self, identifier):
        """Sends a created message to the client for a given resource

        """
        url = self.request.full_url()

        if identifier is not None:
            url = url_path_join(url, identifier)

        location = with_end_slash(url)

        self.set_status(http.client.CREATED.value)
        self.set_header("Location", location)
        self.clear_header('Content-Type')
        self.flush()


class ResourceList(Resource):
    """Handler for URLs without an identifier.
    """
    @gen.coroutine
    def get(self):
        data_layer = self.get_data_layer()
        qs = QSManager(self.request.arguments, self.schema)

        items, total_num = yield data_layer.retrieve_collection(qs)

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
    def post(self):
        data_layer = self.get_data_layer()
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

        identifier = yield data_layer.create_object(data)

        self._send_created_to_client(identifier)

    @gen.coroutine
    def put(self):
        """You cannot PUT on a collection"""
        raise HTTPError(http.client.METHOD_NOT_ALLOWED.value)

    @gen.coroutine
    def delete(self):
        raise HTTPError(http.client.METHOD_NOT_ALLOWED.value)


class ResourceDetails(Resource):
    """Handler for URLs addressing a resource.
    """
    @gen.coroutine
    def get(self, identifier):
        """Retrieves the resource representation."""
        data_layer = self.get_data_layer()
        qs = QSManager(self.request.arguments, self.schema)
        schema = compute_schema(self.schema,
                                {},
                                qs,
                                qs.include)

        obj = yield data_layer.retrieve_object(identifier)

        result = schema.dump(obj).data

        self._send_to_client(result)

    @gen.coroutine
    def patch(self, identifier):
        data_layer = self.get_data_layer()
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

        if str(json_data['data']['id']) != identifier:
            raise exceptions.InvalidIdentifier()

        updated_obj = yield data_layer.update_object(identifier, data)

        result = schema.dump(updated_obj).data

        self._send_to_client(result)

    @gen.coroutine
    def post(self, identifier):
        """This operation is not possible in REST, and results
        in either Conflict or NotFound, depending on the
        presence of a resource at the given URL"""
        data_layer = self.get_data_layer()

        try:
            yield data_layer.retrieve_object(identifier)
        except exceptions.ObjectNotFound:
            raise
        else:
            raise exceptions.ObjectAlreadyPresent()

    @gen.coroutine
    def delete(self, identifier):
        """Deletes the resource."""
        data_layer = self.get_data_layer()

        yield data_layer.delete_object(identifier)

        self._send_to_client(None)


class ResourceRelationship(Resource):

    def get(self, *args, **kwargs):
        """Get a relationship details
        """
        relationship_field, model_relationship_field, related_type_, related_id_field = self._get_relationship_data()
        related_view = self.schema._declared_fields[relationship_field].related_view
        related_view_kwargs = self.schema._declared_fields[relationship_field].related_view_kwargs

        obj, data = self._data_layer.get_relationship(model_relationship_field,
                                                      related_type_,
                                                      related_id_field,
                                                      kwargs)

        for key, value in copy(related_view_kwargs).items():
            if isinstance(value, str) and value.startswith('<') and value.endswith('>'):
                tmp_obj = obj
                for field in value[1:-1].split('.'):
                    tmp_obj = getattr(tmp_obj, field)
                related_view_kwargs[key] = tmp_obj

        result = {'links': {'self': request.path,
                            'related': url_for(related_view, **related_view_kwargs)},
                  'data': data}

        qs = QSManager(request.args, self.schema)
        if qs.include:
            schema = compute_schema(self.schema, dict(), qs, qs.include)

            serialized_obj = schema.dump(obj)
            result['included'] = serialized_obj.data.get('included', dict())

        return result

    def post(self, *args, **kwargs):
        """Add / create relationship(s)
        """
        json_data = request.get_json()

        relationship_field, model_relationship_field, related_type_, related_id_field = self._get_relationship_data()

        if 'data' not in json_data:
            raise BadRequest('/data', 'You must provide data with a "data" route node')
        if isinstance(json_data['data'], dict):
            if 'type' not in json_data['data']:
                raise BadRequest('/data/type', 'Missing type in "data" node')
            if 'id' not in json_data['data']:
                raise BadRequest('/data/id', 'Missing id in "data" node')
            if json_data['data']['type'] != related_type_:
                raise InvalidType('/data/type', 'The type field does not match the resource type')
        if isinstance(json_data['data'], list):
            for obj in json_data['data']:
                if 'type' not in obj:
                    raise BadRequest('/data/type', 'Missing type in "data" node')
                if 'id' not in obj:
                    raise BadRequest('/data/id', 'Missing id in "data" node')
                if obj['type'] != related_type_:
                    raise InvalidType('/data/type', 'The type provided does not match the resource type')

        obj_, updated = self._data_layer.create_relationship(json_data,
                                                             model_relationship_field,
                                                             related_id_field,
                                                             kwargs)

        qs = QSManager(request.args, self.schema)
        includes = qs.include
        if relationship_field not in qs.include:
            includes.append(relationship_field)
        schema = compute_schema(self.schema, dict(), qs, includes)

        if updated is False:
            return '', 204

        result = schema.dump(obj_).data
        if result.get('links', {}).get('self') is not None:
            result['links']['self'] = request.path
        return result, 200

    def patch(self, *args, **kwargs):
        """Update a relationship
        """
        json_data = request.get_json()

        relationship_field, model_relationship_field, related_type_, related_id_field = self._get_relationship_data()

        if 'data' not in json_data:
            raise BadRequest('/data', 'You must provide data with a "data" route node')
        if isinstance(json_data['data'], dict):
            if 'type' not in json_data['data']:
                raise BadRequest('/data/type', 'Missing type in "data" node')
            if 'id' not in json_data['data']:
                raise BadRequest('/data/id', 'Missing id in "data" node')
            if json_data['data']['type'] != related_type_:
                raise InvalidType('/data/type', 'The type field does not match the resource type')
        if isinstance(json_data['data'], list):
            for obj in json_data['data']:
                if 'type' not in obj:
                    raise BadRequest('/data/type', 'Missing type in "data" node')
                if 'id' not in obj:
                    raise BadRequest('/data/id', 'Missing id in "data" node')
                if obj['type'] != related_type_:
                    raise InvalidType('/data/type', 'The type provided does not match the resource type')

        obj_, updated = self._data_layer.update_relationship(json_data,
                                                             model_relationship_field,
                                                             related_id_field,
                                                             kwargs)

        qs = QSManager(request.args, self.schema)
        includes = qs.include
        if relationship_field not in qs.include:
            includes.append(relationship_field)
        schema = compute_schema(self.schema, dict(), qs, includes)

        if updated is False:
            return '', 204

        result = schema.dump(obj_).data
        if result.get('links', {}).get('self') is not None:
            result['links']['self'] = request.path
        return result, 200

    @check_method_requirements
    def delete(self, *args, **kwargs):
        """Delete relationship(s)
        """
        json_data = request.get_json()

        relationship_field, model_relationship_field, related_type_, related_id_field = self._get_relationship_data()

        if 'data' not in json_data:
            raise BadRequest('/data', 'You must provide data with a "data" route node')
        if isinstance(json_data['data'], dict):
            if 'type' not in json_data['data']:
                raise BadRequest('/data/type', 'Missing type in "data" node')
            if 'id' not in json_data['data']:
                raise BadRequest('/data/id', 'Missing id in "data" node')
            if json_data['data']['type'] != related_type_:
                raise InvalidType('/data/type', 'The type field does not match the resource type')
        if isinstance(json_data['data'], list):
            for obj in json_data['data']:
                if 'type' not in obj:
                    raise BadRequest('/data/type', 'Missing type in "data" node')
                if 'id' not in obj:
                    raise BadRequest('/data/id', 'Missing id in "data" node')
                if obj['type'] != related_type_:
                    raise InvalidType('/data/type', 'The type provided does not match the resource type')

        obj_, updated = self._data_layer.delete_relationship(json_data,
                                                             model_relationship_field,
                                                             related_id_field,
                                                             kwargs)

        qs = QSManager(request.args, self.schema)
        includes = qs.include
        if relationship_field not in qs.include:
            includes.append(relationship_field)
        schema = compute_schema(self.schema, dict(), qs, includes)

        status_code = 200 if updated is True else 204
        result = schema.dump(obj_).data
        if result.get('links', {}).get('self') is not None:
            result['links']['self'] = request.path
        return result, status_code

    def _get_relationship_data(self):
        """Get useful data for relationship management
        """
        relationship_field = request.path.split('/')[-1]

        if relationship_field not in get_relationships(self.schema).values():
            raise RelationNotFound('', "{} has no attribute {}".format(self.schema.__name__, relationship_field))

        related_type_ = self.schema._declared_fields[relationship_field].type_
        related_id_field = self.schema._declared_fields[relationship_field].id_field
        model_relationship_field = get_model_field(self.schema, relationship_field)

        return relationship_field, model_relationship_field, related_type_, related_id_field



