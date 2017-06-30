from tornado import gen, log


class BaseDataLayer:
    """Base class for data layers
    To implement a new data layer class, inherit from this subclass
    and reimplement the methods with the appropriate logic.

    The Data Layer exports two member vars: application and current_user.
    They are equivalent to the members in the tornado web handler.
    """

    def __init__(self, kwargs):
        """Initializes the Resource with a given application and user instance

        Parameters
        ----------
        application: web.Application
            The tornado web application
        current_user:
            The current user as passed by the underlying RequestHandler.
        """

        kwargs.pop('class', None)

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.log = log.app_log

    @gen.coroutine
    def create_object(self, data, view_kwargs):
        """Called to create a resource with the given data.
        The member is passed with an instance of Resource, pre-filled
        with the data from the passed (and decoded) payload.
        This member should be responsible for storing or acting on the
        request, and finally setting the resource.identifier value.

        Correspond to a POST operation on the resource collection.

        Parameters
        ----------
        data: dict
            A dict of the data submitted as payload, already validated
            against the schema.

        view_kwargs: dict
            the keyword arguments passed at the view (via the URL
            named capture groups)

        Returns
        -------
        The generated model object. Must be serializable with the schema.

        Raises
        ------
        ObjectAlreadyPresent:
            Raised when the resource cannot be created because of a
            conflicting already existing resource.
        NotImplementedError:
            If the resource does not support the method.
        """
        raise NotImplementedError()

    @gen.coroutine
    def get_object(self, view_kwargs):
        """Called to retrieve a specific resource given its
        identifier. Correspond to a GET operation on the resource URL.

        Parameters
        ----------
        view_kwargs: dict
            The view kwargs as passed by the URL capture groups.

        Returns
        -------
        None

        Raises
        ------
        NotFound:
            Raised if the resource with the given identifier cannot
            be found
        NotImplementedError:
            If the resource does not support the method.
        """
        raise NotImplementedError()

    @gen.coroutine
    def update_object(self, obj, data, view_kwargs):
        """Called to update (partially) a specific Resource given its
        identifier with new data. Correspond to a PATCH operation on the
        Resource URL.

        Parameters
        ----------
        obj:
            The object to patch.
        data: dict
            The validated dict of the data.
        view_kwargs: dict
            The view kwargs as extracted from the URL capture groups.

        Returns
        -------
        True if the object has been modified, False otherwise.

        Raises
        ------
        NotFound:
            Raised if the resource with the given identifier cannot
            be found
        NotImplementedError:
            If the resource does not support the method.
        """
        raise NotImplementedError()

    @gen.coroutine
    def delete_object(self, obj, view_kwargs):
        """Called to delete a specific resource given its identifier.
        Corresponds to a DELETE operation on the resource URL.

        Parameters
        ----------
        obj:
            an object
        view_kwargs: dict
            the kwargs passed at the view via the URL capture groups.

        Returns
        -------
        None

        Raises
        ------
        NotFound:
            Raised if the resource with the given identifier cannot be found
        NotImplementedError:
            If the resource does not support the method.
        """
        raise NotImplementedError()

    @gen.coroutine
    def get_collection(self, qs, view_kwargs):
        """Invoked when a GET request is performed to the collection URL.

        Parameters
        ----------
        qs:
            The QueryManager information
        view_kwargs: dict
            The view kwargs passed by the URL capture groups

        Returns
        -------
        tuple: the total number of objects and the list of extracted objects.

        Raises
        ------
        NotImplementedError:
            If the resource collection does not support the method.
        """
        raise NotImplementedError()

    def create_relationship(self, json_data, relationship_field,
                            related_id_field, view_kwargs):
        """Create a relationship

        Parameters
        ----------
        json_data: dict
            the request params
        relationship_field: str
            the model attribute used for relationship
        related_id_field: str
            the identifier field of the related model
        view_kwargs: dict
            kwargs from the resource view

        Returns
        -------
        boolean: True if relationship have changed else False
        """
        raise NotImplementedError()

    def get_relationship(self, relationship_field, related_type_,
                         related_id_field, view_kwargs):
        """Get information about a relationship

        Parameters
        ----------
        relationship_field: str
            the model attribute used for relationship
        related_type_: str
            the related resource type
        related_id_field: str
            the identifier field of the related model
        view_kwargs: dict
            kwargs from the resource view

        Returns
        -------
        tuple: the object and related object(s)
        """
        raise NotImplementedError()

    def update_relationship(self, json_data, relationship_field,
                            related_id_field, view_kwargs):
        """Update a relationship

        Parameters
        ----------
        json_data: dict
            the request params
        relationship_field: str
            the model attribute used for relationship
        related_id_field: str
            the identifier field of the related model
        view_kwargs: dict
            kwargs from the resource view

        Returns
        -------
        boolean: True if relationship have changed else False
        """
        raise NotImplementedError()

    def delete_relationship(self, json_data, relationship_field,
                            related_id_field, view_kwargs):
        """Delete a relationship

        Parameters
        ----------
        json_data: dict
            the request params
        relationship_field: str
            the model attribute used for relationship
        related_id_field: str
            the identifier field of the related model
        view_kwargs: dict
            kwargs from the resource view
        """
        raise NotImplementedError()

    def query(self, view_kwargs):
        """Construct the base query to retrieve wanted data

        Parameters
        ----------
        view_kwargs: dict
            kwargs from the resource view
        """
        raise NotImplementedError()
