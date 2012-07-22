import os.path
import tornado.options
from tornado.options import options
from tornado.options import define

BASE_DIR = os.path.realpath(os.path.dirname(__file__))

define("debug", True)
define("addr", '127.0.0.1')
define("port", 8888)

define("db_host", "localhost")
define("db_port", 27017)
define("db_name", "lai_dev")
define("db_collection", "server")

define("prv_key", os.path.join(os.path.expanduser('~'), ".ssh/id_rsa"))

try:
    options_file = os.path.join(BASE_DIR, 'options.py')
    tornado.options.parse_config_file(options_file)
except:
    pass

tornado.options.parse_command_line()
