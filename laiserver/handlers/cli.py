# -*- coding: utf-8 -*-

from tornado.web import HTTPError
from laiserver.handlers import BaseHandler
from laiserver.lib import crypto

import base64
import json

try:
    from bson.objectid import ObjectId
except ImportError:
    from pymongo.objectid import ObjectId


class SyncHandler(BaseHandler):

    def post(self):
        data = self.get_argument('data')
        doc  = self._get_doc(data)
        data = self._process(doc)
        self.write(data)

    def _get_doc(self, data):
        enc = base64.b64decode(data)
        msg = crypto.decrypt(enc, self.application.prv_key)
        doc = json.loads(msg)
        return doc

    def _get_data(self, doc):
        pub_key = self._get_pub_key(doc)
        msg  = json.dumps(doc)
        enc  = crypto.encrypt(msg, pub_key)
        data = base64.b64encode(enc)
        return data

    def _process(self, doc):
        self.user = self.get_user(doc['username'])
        if self.user is None:
            args = (doc['username'],)
            msg  = 'Username %s does not exist' % args
            raise HTTPError(500, msg)
        if not self._get_pub_key(doc):
            args = (doc['key_name'], doc['username'])
            msg  = 'Invalid key_name %s for username %s' % args
            raise HTTPError(500, msg)
        return self._delegate(doc)

    def _get_pub_key(self, doc):
        name = doc['key_name']
        pub_keys = self.user['pub_keys']
        if name in pub_keys:
            return pub_keys[name]

    def _delegate(self, doc):
        PROC = {
            'update': self._update,
            'commit': self._commit
        }
        if doc['process'] not in PROC:
            args = (doc['process'], doc['username'])
            msg  = 'Invalid process %s by username %s' % args
            raise HTTPError(500, msg)
        return PROC[doc['process']](doc)

    def _update(self, doc):
        doc['result'] = 'updated ok'
        data = self._get_data(doc)
        return data

    def _commit(self, doc):
        doc['result'] = 'commited ok'
        data = self._get_data(doc)
        return data


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

