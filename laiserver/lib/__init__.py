import pymongo
from laiserver import options

try:
    from bson.objectid import ObjectId
except ImportError:
    from pymongo.objectid import ObjectId


connection = pymongo.Connection(options.db_host, options.db_port)
db = connection[options.db_name]
