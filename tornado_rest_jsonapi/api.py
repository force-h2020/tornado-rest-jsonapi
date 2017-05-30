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

    def route(self, resource, name, url):
        """Registers a Resource.
        The URL must have at least one capture group for the identifier,
        if the resource is a Detail resource.

        http://example.com/api/v1/images/identifier/

        Parameters
        ----------
        resource: Resource
            A subclass of the Resource class
        name: str
            A unique string associated to the view for named linkage.
        url: str
            URL to bind to the resource.

        Raises
        ------
        TypeError:
            if typ is not a subclass of Resource
        """
        if resource is None or not issubclass(resource, Resource):
            raise TypeError("resource must be a subclass of Resource")

        if url in self._register:
            raise ValueError(
                "url {} is already in use by "
                "{}, so it cannot be used by {}".format(
                    url,
                    self._register[url].__name__,
                    resource.__name__
                ))

        self._register[url] = resource
        target_kwargs = dict(
            registry=self,
            base_urlpath=self._base_urlpath
        )

        self._application.wildcard_router.add_rules([
            (
                with_end_slash(url_path_join(self._base_urlpath, url)),
                resource,
                target_kwargs,
                name
            )
        ])
