# -*- coding: utf-8 -*-

import os.path
from tornado.options import define

define("debug", True)
define("addr", '127.0.0.1')
define("port", 8888)

define("db_host", "localhost")
define("db_port", 27017)
define("db_name", "lai_dev")
define("db_collection", "server")

define("pub_key", os.path.join(os.path.expanduser('~'), ".ssh/id_rsa.pub"))
define("prv_key", os.path.join(os.path.expanduser('~'), ".ssh/id_rsa"))
