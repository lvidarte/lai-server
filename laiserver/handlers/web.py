# -*- coding: utf-8 -*-

import tornado.auth
from laiserver.handlers import BaseHandler


class LoginHandler(BaseHandler, tornado.auth.GoogleMixin):
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
        self._save_if_not_exists(user)
        self.redirect('/user')

    def _save_if_not_exists(self, user):
        if self.get_user(user['email']) is None:
            doc = {'username': user['email'],
                   'name'    : user['name'],
                   'pub_keys': {},
                   'last_tid': 0}
            self.db.users.insert(doc)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('username')
        self.redirect('/')


class HomeHandler(BaseHandler):
    def get(self):
        args = {
            'title': 'Home',
            'username': self.current_user,
            'home_active': 'active',
            'user_active': '',
        }
        self.render('home.html', **args)


class UserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.get_user(self.current_user)
        args = {
            'title': 'Home',
            'username': self.current_user,
            'user': user,
            'user_active': 'active',
            'home_active': '',
        }
        self.render('user.html', **args)

    @tornado.web.authenticated
    def post(self):
        key_name = self.get_argument('key_name').strip()
        key_value = self.get_argument('key_value', '').strip()
        user = self.get_user(self.current_user)
        spec = {'username': user['username']}
        pub_keys = user['pub_keys']
        if key_value == '' and key_name in pub_keys:
            del pub_keys[key_name]
        else:
            pub_keys.update({key_name: key_value})
        document = {'$set': {'pub_keys': pub_keys}}
        self.db.users.update(spec, document)
        self.redirect('/user')

