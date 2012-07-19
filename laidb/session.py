from pymongo import Connection
from datetime import datetime, timedelta
from time import sleep

TTL = 10

connection = Connection()
db = connection.test
collection = db.expire


def set_session(user, session_id):
    expire = datetime.now() + timedelta(seconds=TTL)
    spec = {'user': user, 'session_id': session_id}
    document = {'user': user, 'session_id': session_id, 'expire': expire}
    rs = collection.update(spec, document, upsert=True, safe=True)
    return rs

def get_session(user, session_id):
    clean_session()
    spec = {'user': user, 'session_id': session_id}
    fields = {'_id': 0}
    row = collection.find_one(spec, fields)
    return row

def clean_session():
    rs = collection.remove({'expire': {'$lt': datetime.now()}}, safe=True)
    return rs

if __name__ == '__main__':
    import string, random
    def get_session_id(length):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join([random.choice(chars) for x in range(length)])
    user = 'lvidarte'
    session_id = get_session_id(32)
    print "Setting object into session for %d seconds.." % TTL
    set_session(user, session_id)
    print "Getting object.."
    print get_session(user, session_id)
    secs = TTL + 1
    print "Sleeping %d seconds.." % secs
    sleep(secs)
    print "Getting object.."
    print get_session(user, session_id)
