from collections import OrderedDict

from .resource import Resource

from .utils import url_path_join, with_end_slash
from .authenticator import NullAuthenticator


class Api:
    """Main class that registers the defined resources,
    and provides the appropriate handlers for tornado.

    It is also responsible for holding the authenticator,
    the renderer (converts internal representation to
    HTTP response payload) and the parser (converts HTTP
    request payload to internal representation).

    A registry is normally instantiated and held on the
    Tornado Application.
    """

    def __init__(self, application, base_urlpath="/api"):
        """Defines an Api for the web application.

        Parameters
        ----------
        application: web.Application
            A tornado web application
        base_urlpath: str
            A prefix url to be added to all subsequent urls.
        """
        self._application = application
        self._register = OrderedDict()
        self._authenticator = NullAuthenticator
        self._base_urlpath = base_urlpath

    @property
    def authenticator(self):
        return self._authenticator

    @authenticator.setter
    def authenticator(self, authenticator):
        self._authenticator = authenticator

    @property
    def registered(self):
        return self._register

    def route(self, resource, view, *urls, **kwargs):
        """Adds a route for a resource.
        The URL must have at least one capture group for the identifier,
        if the resource is a Detail resource. URLs for REST are typically
        in the form

        http://example.com/api/v1/images/identifier/

        with pluralized names for collections.

        Parameters
        ----------
        resource: Resource
            A subclass of the Resource class
        view: str
            A unique string associated to the view for named linkage.
        *urls: str
            URL to bind to the resource. This URL will be prefixed with the
            base_urlpath as specified at construction, or the default if not
            specified.
        **kwargs: dict
            Additional keyword arguments to pass to the Resource
            while handling the request.

        Raises
        ------
        TypeError:
            if resource is not a subclass of Resource
        ValueError:
            if an URL has already been bound.
        """
        if resource is None or not issubclass(resource, Resource):
            raise TypeError("resource must be a subclass of Resource")

        for url in urls:
            if url in self._register:
                raise ValueError(
                    "url {} is already in use by "
                    "{}, so it cannot be used by {}".format(
                        url,
                        self._register[url].__name__,
                        resource.__name__
                    ))

        for url in urls:
            self._register[url] = resource

            target_kwargs = dict(kwargs)
            target_kwargs.update(
                dict(
                    registry=self,
                    base_urlpath=self._base_urlpath
                )
            )

            self._application.wildcard_router.add_rules([
                (
                    with_end_slash(url_path_join(self._base_urlpath, url)),
                    resource,
                    target_kwargs,
                    view
                )
            ])
