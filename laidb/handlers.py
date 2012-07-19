# -*- coding: utf-8 -*-

from tornado.options import options

import tornado.web
import tornado.auth

import json

try:
    from bson.objectid import ObjectId
except ImportError:
    from pymongo.objectid import ObjectId


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.db = self.application.db
        #self.set_header('Content-Type', 'application/json')

    def get_current_user(self):
        return self.get_secure_cookie('username')

class LoginHandler(tornado.web.RequestHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument('openid.mode', None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Google auth failed")
        self.set_secure_cookie('username', user['email'], expires_days=None)
        self.redirect('/')

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('username')
        self.redirect('/')

class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        args = {
            'title': 'Home',
            'username': self.current_user,
        }
        self.render('home.html', **args)

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

