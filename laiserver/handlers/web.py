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
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lai-server. If not, see <http://www.gnu.org/licenses/>.

import tornado.auth
from laiserver.handlers import BaseHandler
from laiserver import options


class LoginHandler(BaseHandler, tornado.auth.GoogleOAuth2Mixin):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri='http://lai.nerdlabs.com.ar/login',
                code=self.get_argument('code'))
            user = yield self.oauth2_request(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                access_token=access['access_token'])
            self._on_auth(access, user)
        else:
            yield self.authorize_redirect(
                redirect_uri='http://lai.nerdlabs.com.ar/login',
                client_id=options.google_client_id,
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})

    def _on_auth(self, access, user):
        if not user:
            raise tornado.web.HTTPError(500, "Google auth failed")
        self.set_secure_cookie('user', user['email'], expires_days=None)
        self._save_if_not_exists(user)
        self.redirect('/user')

    def _save_if_not_exists(self, user):
        if self.get_user(user['email']) is None:
            doc = {'user'    : user['email'],
                   'name'    : user['name'],
                   'pub_keys': {},
                   'last_tid': 0}
            self.db.users.insert(doc)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('user')
        self.redirect('/')


class HomeHandler(BaseHandler):
    def get(self):
        user = self.get_user(self.current_user)
        args = {
            'title'      : 'Home',
            'user'       : user,
            'home_active': 'active',
            'user_active': '',
        }
        self.render('home.html', **args)


class UserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.get_user(self.current_user)
        args = {
            'title'      : 'User',
            'user'       : user,
            'user_active': 'active',
            'home_active': '',
        }
        self.render('user.html', **args)

    @tornado.web.authenticated
    def post(self):
        key_name = self.get_argument('key_name').strip()
        key_value = self.get_argument('key_value', '').strip()
        user = self.get_user(self.current_user)
        spec = {'user': user['user']}
        pub_keys = user['pub_keys']
        if key_value == '' and key_name in pub_keys:
            del pub_keys[key_name]
        else:
            pub_keys.update({key_name: key_value})
        document = {'$set': {'pub_keys': pub_keys}}
        self.db.users.update(spec, document)
        self.redirect('/user')

