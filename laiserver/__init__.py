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

import os.path
import tornado.options
from tornado.options import options
from tornado.options import define


version = '0.1.0'

define("base_dir", os.path.realpath(os.path.dirname(__file__)))

define("debug", True)
define("addr", '127.0.0.1')
define("port", 8888)

define("db_host", "localhost")
define("db_port", 27017)
define("db_name", "lai_dev")
define("db_collection", "server")

define("prv_key", os.path.join(os.path.expanduser('~'), ".ssh/id_rsa"))

try:
    options_file = os.path.join(options.base_dir, '/etc/default/lai-server')
    tornado.options.parse_config_file(options_file)
except:
    pass

tornado.options.parse_command_line()
