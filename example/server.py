import os

from collections import OrderedDict

from tornado import gen, ioloop, web

from marshmallow_jsonapi import Schema, fields

from tornado_rest_jsonapi import exceptions, Api
from tornado_rest_jsonapi.model_connector import (ModelConnector
                                                  as ModelConnectorBase)
from tornado_rest_jsonapi.resource import ResourceList, ResourceDetails


class ModelConnector(ModelConnectorBase):
    collection = OrderedDict()
    id = 0

    @gen.coroutine
    def create_object(self, data, **kwargs):
        id = str(type(self).id)
        print("Create object with id:", id)
        print("Data:", data)
        data["id"] = id
        self.collection[id] = data
        type(self).id += 1
        return id

    @gen.coroutine
    def retrieve_object(self, identifier, **kwargs):
        if identifier not in self.collection:
            raise exceptions.ObjectNotFound()

        return self.collection[identifier]

    @gen.coroutine
    def update_object(self, identifier, data, **kwargs):
        if identifier not in self.collection:
            raise exceptions.ObjectNotFound()

        self.collection[identifier].update(data)

    @gen.coroutine
    def delete_object(self, identifier, **kwargs):
        if identifier not in self.collection:
            raise exceptions.ObjectNotFound()

        del self.collection[identifier]

    @gen.coroutine
    def retrieve_collection(self, qs, **kwargs):
        pagination = qs.pagination

        number = pagination.get("number", 0)
        size = pagination.get("size", 10)

        interval = slice(number*size, (number+1)*size)

        # if filter_ is not None:
        #     values = [x for x in self.collection.values() if filter_(x)]
        # else:
        #     values = [x for x in self.collection.values()]

        values = [x for x in self.collection.values()][interval]
        return values, len(self.collection.values())


class ApplicationSchema(Schema):
    class Meta:
        type_ = 'application'
    id = fields.Int()
    name = fields.String(required=True)


class ApplicationModel(ModelConnector):
    pass


class ApplicationDetails(ResourceDetails):
    schema = ApplicationSchema
    model_connector = ApplicationModel


class ApplicationList(ResourceList):
    schema = ApplicationSchema
    model_connector = ApplicationModel


class MainHandler(web.RequestHandler):
    def get(self, *args):
        self.render('index.html')

server = web.Application([
    (r'/', MainHandler),
    (r'/static/(.*)', web.StaticFileHandler, {'path': 'static'})
])

jsonapi = Api(server, base_urlpath='/api')
jsonapi.route(ApplicationList, 'application_list', '/applications/')
jsonapi.route(ApplicationDetails, 'application_detail', '/applications/(.*)')

server.listen(8888)
ioloop.IOLoop.current().start()
