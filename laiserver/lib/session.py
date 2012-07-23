from datetime import datetime, timedelta
from time import sleep
from laiserver.lib import db, ObjectId


TTL = 10


def create(doc):
    spec = {'user'   : doc['user'],
            'process': doc['process'],
            'expire' : get_expire_time()}
    _id = db.sessions.insert(spec)
    return str(_id)

def get_expire_time():
    expire_time = datetime.now() + timedelta(seconds=TTL)
    return expire_time

def update(doc):
    remove_expired()
    spec = {'_id' : ObjectId(doc['session_id']),
            'user': doc['user']}
    document = {'process': doc['process'],
                'expire' : get_expire_time()}
    rs = db.sessions.update(spec, {'$set': document}, safe=True)
    return rs['n'] == 1

def remove_expired():
    spec = {'expire': {'$lt': datetime.now()}}
    rs = db.sessions.remove(spec, safe=True)
    return rs


if __name__ == '__main__':
    doc = {'user'   : 'lvidarte@gmail.com',
           'process': 'update'}
    doc['session_id'] = create(doc)
    sleep(TTL)
    print update(doc)
