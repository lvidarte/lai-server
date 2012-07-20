import logging
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.options


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('username')

class WelcomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write("hello " + self.current_user)

class LoginGoogleHandler(tornado.web.RequestHandler, tornado.auth.GoogleMixin):
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

if __name__ == '__main__':
    settings = {
        'debug'        : True,
        'cookie_secret': '8577a601e2418c0d38afe28fdff932be09f6671ad3dec97ce62ae34a8c95a3c5',
        'login_url'    : '/login',
    }
    application = tornado.web.Application([
        (r'/', WelcomeHandler),
        (r'/login', LoginGoogleHandler),
        (r'/logout', LogoutHandler),
    ], **settings)

    tornado.options.parse_command_line()
    application.listen(8888)
    logging.info('server started')
    tornado.ioloop.IOLoop.instance().start()
