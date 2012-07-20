import sys
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
    doc = {'username': 'lvidarte@gmail.com',
           'key_name': 'howl',
           'process' : 'update',
           'docs'    : [1, 2, 3]}
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
        print doc['result']

