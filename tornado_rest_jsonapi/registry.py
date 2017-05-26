from collections import OrderedDict

from .resource import Resource

from .utils import url_path_join, with_end_slash
from .authenticator import NullAuthenticator


class Registry:
    """Main class that registers the defined resources,
    and provides the appropriate handlers for tornado.

    It is also responsible for holding the authenticator,
    the renderer (converts internal representation to
    HTTP response payload) and the parser (converts HTTP
    request payload to internal representation).

    A registry is normally instantiated and held on the
    Tornado Application.
    """

    def __init__(self):
        self._register = OrderedDict()
        self._authenticator = NullAuthenticator

    @property
    def authenticator(self):
        return self._authenticator

    @authenticator.setter
    def authenticator(self, authenticator):
        self._authenticator = authenticator

    @property
    def registered(self):
        return self._register

    def register(self, resource, url):
        """Registers a Model Connector.
        The associated resource will be used to determine the URL
        representing the resource collections. For example, a resource Image
        will have URLs of the type

        http://example.com/api/v1/images/identifier/

        Parameters
        ----------
        resource: Resource
            A subclass of the Resource class

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

    def api_handlers(self, base_urlpath, version="v1"):
        """Returns the API handlers for the interface.
        Add these handlers to your application to provide an
        interface to your Resources.


        Parameters
        ----------
        base_urlpath: str
            The base url path to serve
        version: str
            A string identifying the version of the API.

        Notes
        -----
        The current implementation does not support multiple API versions yet.
        The version option is only provided for futureproofing.
        """
        init_args = dict(
            registry=self,
            base_urlpath=base_urlpath,
        )

        handlers = []
        for url, resource in self._register.items():
            handlers.append(
                (
                    with_end_slash(
                        url_path_join(base_urlpath,
                                      "api",
                                      version,
                                      url
                                      )
                    ),
                    resource,
                    init_args
                )
            )

        return handlers
