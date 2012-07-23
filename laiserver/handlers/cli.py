from tornado.web import HTTPError
from laiserver.handlers import BaseHandler
from laiserver.lib import crypto
from laiserver.lib import session
from laiserver.lib import ObjectId

import base64
import json


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
        msg = None
        self.user = self.get_user(doc['username'])
        if self.user is None:
            args = (doc['username'],)
            msg  = 'Username %s does not exist' % args
        if not self._get_pub_key(doc):
            args = (doc['key_name'], doc['username'])
            msg  = 'Invalid key_name %s for username %s' % args
        if 'tid' not in doc:
            msg  = 'No tid in doc request'
        if msg:
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
        doc['session_id'] = session.create(doc)
        doc['docs'] = self._get_update_docs(doc)
        data = self._get_data(doc)
        return data

    def _commit(self, doc):
        if len(self._get_update_docs(doc)) == 0:
            if session.update(doc):
                tid = self._get_next_tid(doc)
                docs = []
                for doc_ in doc['docs']:
                    doc__ = self._process_commit(doc_, tid)
                    docs.append(doc__)
                doc['docs'] = docs[:]
            else:
                del doc['docs']
                doc['error'] = 'Session expired'
        else:
            del doc['docs']
            doc['error'] = 'You must update first'
        data = self._get_data(doc)
        return data

    def _get_next_tid(self, doc):
        query = {'username': doc['username']}
        update = {'$inc': {'last_tid': 1}}
        row = self.db.users.find_and_modify(query, update, upsert=True, new=True)
        return row['last_tid']

    def _get_update_docs(self, doc):
        docs = []
        query = {'username': doc['username'],
                 'tid'     : {'$gt': doc['tid']}}
        cur = self.db.docs.find(query)
        for row in cur:
            row['sid'] = str(row['_id'])
            del row['_id']
            docs.append(row)
        return docs

    def _process_commit(self, doc, tid, username):
        _doc = {'tid'     : tid,
                'data'    : doc['data'],
                'public'  : doc['public']}
        if doc['sid'] is not None:
            _id  = ObjectId(doc['sid'])
            self.coll.update({'_id': _id}, {'$set': _doc})
        else:
            _doc['username'] = username
            _id  = self.coll.insert(_doc)
        __doc = {'id'  : doc['id'],
                 'sid' : str(_id),
                 'tid' : tid}
        return __doc

