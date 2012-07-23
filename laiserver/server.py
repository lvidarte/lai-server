# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web

from laiserver import options
from laiserver.routes import routes

import os.path
import pymongo
import logging


class Application(tornado.web.Application):
    def __init__(self):
        self.conn = pymongo.Connection(options.db_host, options.db_port)
        self.db = self.conn[options.db_name]
        self.prv_key = open(options.prv_key, 'r').read()
        settings = {
            'debug'        : options.debug,
            'cookie_secret': '8577a601e2418c0d38afe28fdff932be09f6671ad3',
            'login_url'    : '/login',
            'static_path'  : os.path.join(options.base_dir, 'static'),
            'template_path': os.path.join(options.base_dir, 'templates'),
            'gzip'         : True,
        }
        super(Application, self).__init__(routes, **settings)


if __name__ == '__main__':
    application = Application()
    application.listen(options.port, options.addr)
    logging.info('lai server started')
    tornado.ioloop.IOLoop.instance().start()

