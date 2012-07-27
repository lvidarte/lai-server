# -*- coding: utf-8 -*-

# This file is part of lai-server.
#
# lai-server is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.
#
# lai-server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lai-server. If not, see <http://www.gnu.org/licenses/>.

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
        error = self._validate(doc)
        if error:
            raise HTTPError(500, error)
        return self._delegate(doc)

    def _validate(self, doc):
        self.user = self.get_user(doc['user'])
        if self.user is None:
            return 'User %s does not exist' % doc['user']
        if not self._get_pub_key(doc):
            args  = (doc['key_name'], doc['user'])
            return 'Invalid key_name %s for user %s' % args
        if 'last_tid' not in doc:
            return 'No last_tid in doc request'

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
            args  = (doc['process'], doc['user'])
            error = 'Invalid process %s by user %s' % args
            raise HTTPError(500, error)
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
                subdocs = []
                for subdoc in doc['docs']:
                    sdoc = self._do_commit(subdoc, tid, doc['user'])
                    subdocs.append(sdoc)
                doc['docs'] = subdocs[:]
            else:
                del doc['docs']
                doc['error'] = 'Session expired'
        else:
            del doc['docs']
            doc['error'] = 'You must update first'
        data = self._get_data(doc)
        return data

    def _get_next_tid(self, doc):
        query  = {'user': doc['user']}
        update = {'$inc': {'last_tid': 1}}
        row = self.db.users.find_and_modify(query, update, upsert=True, new=True)
        return row['last_tid']

    def _get_update_docs(self, doc):
        docs  = []
        query = {'user': doc['user'],
                 'tid' : {'$gt': doc['last_tid']}}
        fields = {'user': 0}
        cur = self.db.docs.find(query, fields)
        for row in cur:
            row['sid'] = str(row['_id'])
            del row['_id']
            docs.append(row)
        return docs

    def _do_commit(self, subdoc, tid, user):
        sdoc = {'tid'   : tid,
                'data'  : subdoc['data'],
                'public': subdoc['public']}
        if subdoc['sid']:
            _id  = ObjectId(subdoc['sid'])
            self.db.docs.update({'_id': _id}, {'$set': sdoc})
        else:
            sdoc['user'] = user
            _id  = self.db.docs.insert(sdoc, safe=True)
        return {'id' : subdoc['id'], 'sid': str(_id), 'tid': tid}

