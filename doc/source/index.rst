Tornado-WebAPI documentation
============================

Tornado WebAPI is a Resource based Create-Retrieve-Update-Delete framework
built on top of Tornado.

It provides a WebAPI endpoint and the javascript objects to manipulate the resources.

Example
-------

In python, you reimplement a `Resource` object, and define its behavior for the various
actions::

    class MyResource(Resource):
        @gen.coroutine
        @authenticated
        def delete(self, identifier):
            # define what to do when deleting the resource.

        @gen.coroutine
        @authenticated
        def create(self, representation):
            # Define what to do when create happens


In the Web Application, create a registry, register your resources, and get the handlers::

        base_urlpath = '/basepath/'
        reg = Registry()
        reg.register(MyResource)
        handlers = reg.api_handlers(base_urlpath)

These handlers are installed on tornado as usual, and provide collection and resource
URLs, like::

    /basepath/api/v1/myresources/
    
JavaScript code (needs require.js and jquery properly setup) is found at::
 
    /basepath/jsapi/v1/resources.js

it's a module that can be used to create the resource by passing a object
representation, as in::

    require('resources'), function(resources) {
        resources.MyResource.create({ foo: bar })
        // or
        resources.MyResource.delete("resourceid");
    }

.. toctree::
   :maxdepth: 1

   api
   license
