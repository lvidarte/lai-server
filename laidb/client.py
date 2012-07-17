import sys
import os.path
import urllib
import urllib2
import base64

from cryptor import encrypt


SERVER_URL = 'http://127.0.0.1:8888/'
PUBLIC_KEY = os.path.join(os.path.expanduser('~'), ".ssh/id_rsa.pub")


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
    message = open(sys.argv[1], 'r').read()
    message = message.encode('utf8')
    data = encrypt(message, PUBLIC_KEY)
    data = base64.b64encode(data)
    try:
        print fetch(data)
    except:
        print "Error"

