# -*- coding: utf-8 -*-

from tornado.options import options
from laiserver.handlers import BaseHandler

import json

try:
    from bson.objectid import ObjectId
except ImportError:
    from pymongo.objectid import ObjectId


class SyncHandler(BaseHandler):
    def get(self):
        self.write("hello world")

class OldHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super(OldHandler, self).__init__(*args, **kwargs)
        self.coll = self.application.db[options.db_collection]
        self.set_header('Content-Type', 'application/json')

    def get(self, user, tid):
        tid = int(tid)
        docs = self._get_update_docs(user, tid)
        self.write(json.dumps({'docs': docs}))

    def _get_update_docs(self, user, tid):
        docs = []
        cur = self.coll.find({'tid': {'$gt': tid},
                              '$or': [{'users':    {'$in': [user]}},
                                      {'usersdel': {'$in': [user]}}]
                             })

        for doc in cur:
            _doc = {'sid'     : str(doc['_id']),
                    'tid'     : doc['tid'],
                    'data'    : doc['data'],
                    'keys'    : doc['keys'],
                    'users'   : doc['users'],
                    'usersdel': doc['usersdel']}
            docs.append(_doc)
        return docs

    def post(self, user, tid):
        tid = int(tid)
        docs = json.loads(self.get_argument('docs'))
        if len(self._get_update_docs(user, tid)) == 0:
            tid = self._get_next_tid()
            _docs = []
            for doc in docs:
                _doc = self._process(doc, tid)
                _docs.append(_doc)
            self.write(json.dumps({'docs': _docs}))
        else:
            self.write(json.dumps({'error': 'you must update first'}))

    def _get_next_tid(self):
        query = {'_id': options.db_collection}
        update = {'$inc': {'last_tid': 1}}
        collection = self.application.db['counter']
        row = collection.find_and_modify(query, update, upsert=True, new=True)
        return row['last_tid']

    def _process(self, doc, tid):
        _doc = {'tid'     : tid,
                'data'    : doc['data'],
                'keys'    : doc['keys'],
                'users'   : doc['users'],
                'usersdel': doc['usersdel']}

        if doc['sid'] is not None:
            _id  = ObjectId(doc['sid'])
            self.coll.update({'_id': _id}, {'$set': _doc})
        else:
            _id  = self.coll.insert(_doc)

        _doc = {'id'      : doc['id'],
                'sid'     : str(_id),
                'tid'     : tid,
                'users'   : doc['users'],
                'usersdel': doc['usersdel']}
        return _doc

