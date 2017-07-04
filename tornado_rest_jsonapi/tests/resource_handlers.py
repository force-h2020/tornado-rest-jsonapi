from collections import OrderedDict

from marshmallow_jsonapi import Schema, fields
from tornado import gen

from tornado_rest_jsonapi import exceptions
from tornado_rest_jsonapi.data_layers.base import BaseDataLayer
from tornado_rest_jsonapi.resource import (
    ResourceDetails,
    ResourceList,
    ResourceRelationship)


class WorkingDataLayer(BaseDataLayer):
    """Base class for tests. Still missing the resource_class
    that must be set in the derived class."""

    collection = OrderedDict()
    id = 0

    @gen.coroutine
    def create_object(self, data, view_kwargs):
        id = str(type(self).id)
        data["id"] = id
        self.collection[id] = data
        type(self).id += 1
        return data

    @gen.coroutine
    def get_object(self, kwargs):
        identifier = kwargs.get("id")
        if identifier not in self.collection:
            raise exceptions.ObjectNotFound()

        return self.collection[identifier]

    @gen.coroutine
    def update_object(self, obj, data, view_kwargs):
        obj.update(data)
        return True

    @gen.coroutine
    def delete_object(self, obj, view_kwargs):
        identifier = view_kwargs.get("id")

        if identifier not in self.collection:
            raise exceptions.ObjectNotFound()

        del self.collection[identifier]

    @gen.coroutine
    def get_collection(self, qs, view_kwargs):
        pagination = qs.pagination

        number = pagination.get("number", 0)
        size = pagination.get("size", 10)

        interval = slice(number*size, (number+1)*size)

        # if filter_ is not None:
        #     values = [x for x in self.collection.values() if filter_(x)]
        # else:
        #     values = [x for x in self.collection.values()]

        values = [x for x in self.collection.values()][interval]
        return len(self.collection.values()), values


class UserSchema(Schema):
    class Meta:
        type_ = "user"
        self_url = '/api/v1/users/{id}/'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/api/v1/users/'

    id = fields.Int()
    name = fields.String(required=True)
    age = fields.Int(required=True)


class UserDetails(ResourceDetails):
    schema = UserSchema
    data_layer = {
        "class": WorkingDataLayer
    }


class UserList(ResourceList):
    schema = UserSchema
    data_layer = {
        "class": WorkingDataLayer,
    }


class TeamSchema(Schema):
    name = fields.String()
    users = fields.Relationship(
        self_url='/teams/{team_id}/relationships/users',
        self_url_kwargs={'team_id': '<id>'},
        related_url='/users/{user_id}/',
        related_url_kwargs={"user_id": "<id>"},
        many=True,
        schema=UserSchema,
        type_='user',
        include_resource_linkage=True,
    )


class TeamDetails(ResourceDetails):
    schema = TeamSchema
    data_layer = {
        "class": WorkingDataLayer
    }


class TeamList(ResourceList):
    schema = TeamSchema
    data_layer = {
        "class": WorkingDataLayer,
    }


class TeamRelationship(ResourceRelationship):
    schema = TeamSchema
    data_layer = {
        "class": WorkingDataLayer,
    }
