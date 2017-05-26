import socket

import tornado.netutil
import tornado.testing
from tornado import gen


# Workaround for tornado bug #1573, already fixed in master, but not yet
# available. Remove when upgrading tornado.
def bind_unused_port(reuse_port=False):
    """Binds a server socket to an available port on localhost.

    Returns a tuple (socket, port).
    """
    sock = tornado.netutil.bind_sockets(None,
                                        '127.0.0.1',
                                        family=socket.AF_INET,
                                        reuse_port=reuse_port)[0]
    port = sock.getsockname()[1]
    return sock, port


class AsyncHTTPTestCase(tornado.testing.AsyncHTTPTestCase):
    """Base class workaround for the above condition."""
    def setUp(self):
        self._bind_unused_port_orig = tornado.testing.bind_unused_port
        tornado.testing.bind_unused_port = bind_unused_port

        def cleanup():
            tornado.testing.bind_unused_port = self._bind_unused_port_orig

        self.addCleanup(cleanup)

        super().setUp()


def mock_coro_new_callable(return_value=None, side_effect=None):
    """Creates a patch suitable callable that returns a coroutine
    with appropriate return value and side effect."""

    coro = mock_coro_factory(return_value, side_effect)

    def new_callable():
        return coro

    return new_callable


def mock_coro_factory(return_value=None, side_effect=None):
    """Creates a mock coroutine with a given return value"""
    @gen.coroutine
    def coro(*args, **kwargs):
        coro.called = True
        yield gen.sleep(0.1)
        if side_effect:
            if isinstance(side_effect, Exception):
                raise side_effect
            else:
                side_effect(*args, **kwargs)
        return coro.return_value

    coro.called = False
    coro.return_value = return_value
    return coro
