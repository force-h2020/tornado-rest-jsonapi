from tornado import gen


class Authenticator:
    @classmethod
    @gen.coroutine
    def authenticate(cls, handler):
        """Performs authentication of the access"""
        raise NotImplementedError("Missing implementation for authenticate")


class NullAuthenticator(Authenticator):
    """Authenticator class for the web handlers that does nothing and
    returns None"""

    @classmethod
    @gen.coroutine
    def authenticate(cls, handler):
        """Called by the handler to authenticate the user.
        The handler passes itself as an argument, and expects a valid
        handler.current_user value, or None.

        Note that returning None does not mean that the API will reject
        the request. Just that the current_user is unrecognized.
        Individual Resources must then adapt their behavior according to
        this information"""
        return None
