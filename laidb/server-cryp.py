import os.path
import logging
import tornado.ioloop
import tornado.web
import tornado.options
import base64

from cryptor import decrypt

PRIVATE_KEY = os.path.join(os.path.expanduser('~'), ".ssh/id_rsa")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hola")

    def post(self):
        data = self.get_argument('data')
        data = base64.b64decode(data)
        message = decrypt(data, PRIVATE_KEY)
        message = message.decode('utf8')
        print message

if __name__ == '__main__':
    application = tornado.web.Application([
        (r'/', MainHandler),
    ], debug=True)

    tornado.options.parse_command_line()
    application.listen(8888)
    logging.info('server started')
    tornado.ioloop.IOLoop.instance().start()
