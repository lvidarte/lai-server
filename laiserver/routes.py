from laiserver import handlers

routes = [
    (r'/',       handlers.HomeHandler),
    (r'/login',  handlers.LoginHandler),
    (r'/logout', handlers.LogoutHandler),

    #(r'/(\w+)/(\d+)', handlers.OldHandler)
]
