from collections import OrderedDict

from marshmallow_jsonapi import Schema, fields
from tornado import gen
from tornadowebapi import exceptions
from tornadowebapi.model_connector import ModelConnector
from tornadowebapi.resource import ResourceDetails, ResourceList


class WorkingModelConn(ModelConnector):
    """Base class for tests. Still missing the resource_class
    that must be set in the derived class."""

    collection = OrderedDict()
    id = 0

    @gen.coroutine
    def create_object(self, data, **kwargs):
        id = str(type(self).id)
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


class StudentSchema(Schema):
    class Meta:
        type_ = "student"
    id = fields.Int()
    name = fields.String(required=True)
    age = fields.Int(required=True)


class StudentModelConn(WorkingModelConn):
    pass


class StudentDetails(ResourceDetails):
    schema = StudentSchema
    model_connector = StudentModelConn


class StudentList(ResourceList):
    schema = StudentSchema
    model_connector = StudentModelConn


# class Teacher(Schema):
#     name = fields.String()
#     age = fields.Int(required=False)
#     discipline = fields.List(fields.String())
#
#
# class TeacherModelConn(ModelConnector):
#     pass
#
#
# class TeacherDetails(ResourceDetails):
#     schema = Teacher
#     model_connector = TeacherModelConn
#
#
# class TeacherList(ResourceDetails):
#     schema = Teacher
#     model_connector = TeacherModelConn
#
#
# class Person(Schema):
#     name = fields.String()
#     age = fields.Int()
#
#
# class City(Schema):
#     name = fields.String()
#     mayor = fields.Nested(Person())
#
#
# class CityModelConn(WorkingModelConn):
#     pass
#
#
# class CityDetails(ResourceDetails):
#     schema = City
#     model_connector = CityModelConn
#
#
# class ServerInfo(Schema):
#     uptime = fields.Int()
#     status = fields.String()
#
#
# class ServerInfoModelConn(SingletonModelConn):
#     resource_class = ServerInfo
#
#
# class ServerInfoDetails(ResourceSingletonDetails):
#     schema = ServerInfo
#     model_connector = ServerInfoModelConn
#
#
# class UnsupportAll(Schema):
#     pass
#
#
# class UnsupportAllModelConn(ModelConnector):
#     pass
#
#
# class UnsupportAllDetails(ResourceDetails):
#     schema = UnsupportAll
#     model_connector = UnsupportAllModelConn
#
#
# class UnsupportAllList(ResourceList):
#     schema = UnsupportAll
#     model_connector = UnsupportAllModelConn
#
#
# class Unprocessable(Schema):
#     pass
#
#
# class UnprocessableModelConn(ModelConnector):
#     @gen.coroutine
#     def create_object(self, instance, **kwargs):
#         raise exceptions.BadRepresentation("unprocessable", foo="bar")
#
#     @gen.coroutine
#     def replace_object(self, instance, **kwargs):
#         raise exceptions.BadRepresentation("unprocessable", foo="bar")
#
#     @gen.coroutine
#     def retrieve_object(self, instance, **kwargs):
#         raise exceptions.BadRepresentation("unprocessable", foo="bar")
#
#     @gen.coroutine
#     def retrieve_collection(
#             self, items_response, offset=None, limit=None, **kwargs):
#         raise exceptions.BadRepresentation("unprocessable", foo="bar")
#
#
# class UnprocessableDetails(ResourceDetails):
#     schema = Unprocessable
#     model_connector = UnprocessableModelConn
#
#
# class UnprocessableList(ResourceList):
#     schema = Unprocessable
#     model_connector = UnprocessableModelConn
#
#
# class UnsupportsCollection(Schema):
#     pass
#
#
# class UnsupportsCollectionModelConn(ModelConnector):
#
#     @gen.coroutine
#     def items(self, items_response, offset=None, limit=None, **kwargs):
#         raise NotImplementedError()
#
#
# class UnsupportsCollectionList(ResourceList):
#     schema = UnsupportsCollection
#     model_connector = UnsupportsCollectionModelConn
#
#
# class Broken(Schema):
#     pass
#
#
# class BrokenModelConn(ModelConnector):
#     @gen.coroutine
#     def boom(self, *args):
#         raise Exception("Boom!")
#
#     create_object = boom
#     retrieve_object = boom
#     replace_object = boom
#     delete_object = boom
#     retrieve_collection = boom
#
#
# class BrokenDetails(ResourceDetails):
#     schema = Broken
#     model_connector = BrokenModelConn
#
#
# class BrokenList(ResourceList):
#     schema = Broken
#     model_connector = BrokenModelConn
#
#
# class AlreadyPresent(Schema):
#     pass
#
#
# class AlreadyPresentModelConn(ModelConnector):
#
#     @gen.coroutine
#     def create_object(self, *args, **kwargs):
#         raise exceptions.Exists()
#
#
# class AlreadyPresentDetails(ResourceDetails):
#     schema = AlreadyPresent
#     model_connector = AlreadyPresentModelConn
#
#
# class AlreadyPresentList(ResourceList):
#     schema = AlreadyPresent
#     model_connector = AlreadyPresentModelConn
#
#
# class Sheep(Schema):
#     @classmethod
#     def collection_name(cls):
#         return "sheep"
#
#
# class SheepModelConn(ModelConnector):
#     """Sheep plural is the same as singular."""
#
#
# class SheepDetails(ResourceDetails):
#     schema = Sheep
#     model_connector = SheepModelConn
#
#
# class Octopus(Schema):
#     @classmethod
#     def collection_name(cls):
#         return "octopi"
#
#
# class OctopusModelConn(ModelConnector):
#     """Octopus plural is a matter of debate."""
#     resource_class = Octopus
#
#
# class OctopusDetails(ResourceDetails):
#     schema = Octopus
#     model_connector = OctopusModelConn
#
#
# class Frobnicator(Schema):
#     pass
#
#
# class FrobnicatorModelConn(ModelConnector):
#     """A weird name to test if it's kept"""
#
#
# class FrobnicatorDetails(ResourceDetails):
#     schema = Frobnicator
#     model_connector = FrobnicatorModelConn
