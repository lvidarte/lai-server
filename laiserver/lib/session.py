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

from datetime import datetime, timedelta
from time import sleep
from laiserver.lib import db, ObjectId


TTL = 120


def create(doc):
    spec = {'user'   : doc['user'],
            'process': doc['process'],
            'expire' : get_expire_time()}
    result = db.sessions.insert_one(spec)
    return str(result.inserted_id)

def get_expire_time():
    expire_time = datetime.now() + timedelta(seconds=TTL)
    return expire_time

def update(doc):
    remove_expired()
    spec = {'_id' : ObjectId(doc['session_id']),
            'user': doc['user']}
    document = {'process': doc['process'],
                'expire' : get_expire_time()}
    result = db.sessions.update_one(spec, {'$set': document})
    return result.matched_count == 1

def remove_expired():
    spec = {'expire': {'$lt': datetime.now()}}
    rs = db.sessions.delete_one(spec)
    return rs


if __name__ == '__main__':
    doc = {'user'   : 'lvidarte@gmail.com',
           'process': 'update'}
    doc['session_id'] = create(doc)
    sleep(TTL)
    print update(doc)
