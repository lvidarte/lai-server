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

import pymongo
from laiserver import options

try:
    from bson.objectid import ObjectId
except ImportError:
    from pymongo.objectid import ObjectId


client = pymongo.MongoClient(options.db_host, options.db_port)
db = client[options.db_name]
