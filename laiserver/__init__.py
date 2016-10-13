# -*- coding: utf-8 -*-

# Author: Leo Vidarte <http://nerdlabs.com.ar>
#
# This file is part of lai-server.
#
# lai-server is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.
#
# lai-server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lai-server. If not, see <http://www.gnu.org/licenses/>.

import os.path
import tornado.options
from tornado.options import options
from tornado.options import define


version = '0.1.1'

define("base_dir", os.path.realpath(os.path.dirname(__file__)))
define("home_dir", os.path.expanduser('~'))

define("debug", True)
define("addr", '127.0.0.1')
define("port", 8888)

# Mongo
define("db_host", "localhost")
define("db_port", 27017)
define("db_name", "lai_server")

# Google auth
define("google_client_id", "")
define("google_client_secret", "")

define("prv_key", os.path.join(options.home_dir, ".ssh/id_rsa"))

try:
    options_file = os.path.join(options.home_dir, '.lai-server')
    tornado.options.parse_config_file(options_file)
except:
    pass

tornado.options.parse_command_line()
