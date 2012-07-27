# -*- coding: utf-8 -*-

# This file is part of lai-server.
#
# lai-server is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.
#
# lai-server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lai-server. If not, see <http://www.gnu.org/licenses/>.

import tornado.ioloop
import tornado.web

from laiserver import version
from laiserver import options
from laiserver.routes import routes

import os.path
import logging


class Application(tornado.web.Application):
    def __init__(self):
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
    addr, port = options.addr, options.port
    application.listen(port, addr)
    logging.info('lai server %s started at %s:%s' % (version, addr, port))
    tornado.ioloop.IOLoop.instance().start()

