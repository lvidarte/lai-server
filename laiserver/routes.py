from laiserver.handlers import web, cli

routes = [
    (r'/',       web.HomeHandler),
    (r'/login',  web.LoginHandler),
    (r'/logout', web.LogoutHandler),
    
    (r'/user',   web.UserHandler),

    (r'/sync',   cli.SyncHandler),
]
