from pymongo import Connection
from datetime import datetime, timedelta
from time import sleep
from laiserver import options

try:
    from bson.objectid import ObjectId
except ImportError:
    from pymongo.objectid import ObjectId

TTL = 10

connection = Connection()
db = connection[options.db_name]


def create(doc):
    spec = {'username': doc['username'],
            'process' : doc['process'],
            'expire'  : get_expire_time()}
    _id = db.sessions.insert(spec)
    return str(_id)

def get_expire_time():
    expire_time = datetime.now() + timedelta(seconds=TTL)
    return expire_time

def update(doc):
    remove_expired()
    spec = {'_id'     : ObjectId(doc['session_id']),
            'username': doc['username']}
    document = {'process': doc['process'],
                'expire' : get_expire_time()}
    rs = db.sessions.update(spec, {'$set': document}, safe=True)
    return rs['n'] == 1

def remove_expired():
    spec = {'expire': {'$lt': datetime.now()}}
    rs = db.sessions.remove(spec, safe=True)
    return rs

if __name__ == '__main__':
    doc = {'username': 'lvidarte@gmail.com',
           'process' : 'update'}
    doc['session_id'] = create(doc)
    sleep(TTL)
    print update(doc)
