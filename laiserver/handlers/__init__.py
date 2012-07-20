# -*- coding: utf-8 -*-

import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.db = self.application.db
        #self.set_header('Content-Type', 'application/json')

    def get_current_user(self):
        return self.get_secure_cookie('username')

