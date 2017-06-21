Tornado-REST-JSONAPI documentation
==================================

Tornado REST JSONAPI is a Resource based Create-Retrieve-Update-Delete
framework built on top of Tornado.

Introduction
------------

To define a Resource, you need three components:

- A ``Schema``, that defines the input and output structure of the Resource
- A ``ModelConnector``, that defines how to transform a REST request into
  an action on the Model object.
- and A ``Resource`` subclass, which combines the two above and converts the
  web request into an appropriate form for manipulation by the ModelConnector.

The binding is defined declaratively, and the resource must be registered
through an Api object. This object normally resides on your Tornado
application.

Tornado-REST-JSONAPI is similar, but not equal, to Flask-REST-JSONAPI.
Some differences exists in nomenclature to accommodate for the intrinsic
difference between Flask and Tornado, but the overall design is similar.
We refer to the documentation of Flask-REST-JSONAPI for a general understanding.





.. toctree::
   :maxdepth: 1

   api
   license
