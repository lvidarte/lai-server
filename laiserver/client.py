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

import os.path
import urllib
import urllib2
import base64
import json

from laiserver.lib import crypto


SERVER_URL = 'http://127.0.0.1:8888/sync'
PUB_KEY_FILE = os.path.join(os.path.expanduser('~'), ".ssh/id_rsa.pub")
PUB_KEY = open(PUB_KEY_FILE).read()
PRV_KEY_FILE = os.path.join(os.path.expanduser('~'), ".ssh/id_rsa")
PRV_KEY = open(PRV_KEY_FILE).read()


def fetch(data=None):
    url = SERVER_URL
    if data is not None:
        data = urllib.urlencode({'data': data})
        req = urllib2.Request(url, data)
    else:
        req = url
    res = urllib2.urlopen(req)
    return res.read()

if __name__ == '__main__':
    doc = {'user'      : 'lvidarte@gmail.com',
           'key_name'  : 'howl',
           'session_id': None,
           'process'   : 'update',
           'last_tid'  : 0,
           'docs'      : []}
    msg  = json.dumps(doc)
    enc  = crypto.encrypt(msg, PUB_KEY)
    data = base64.b64encode(enc)
    try:
        data = fetch(data)
    except:
        print "Fetch error"
    else:
        enc  = base64.b64decode(data)
        msg  = crypto.decrypt(enc, PRV_KEY)
        doc  = json.loads(msg)
        print doc['session_id']

    import time
    time.sleep(9)

    # Commit
    doc['process'] = 'commit'
    msg  = json.dumps(doc)
    enc  = crypto.encrypt(msg, PUB_KEY)
    data = base64.b64encode(enc)
    try:
        data = fetch(data)
    except:
        print "Fetch error"
    else:
        enc  = base64.b64decode(data)
        msg  = crypto.decrypt(enc, PRV_KEY)
        doc  = json.loads(msg)
        print doc['session_id']

