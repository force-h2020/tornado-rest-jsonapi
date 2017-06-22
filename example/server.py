import tornado.ioloop
import tornado.web


server = tornado.web.Application([
    (r'/(.*)', tornado.web.StaticFileHandler, {"path": "index.html"})
])

server.listen(8888)
tornado.ioloop.IOLoop.current().start()
