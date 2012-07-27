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

from laiserver.handlers import web, cli

routes = [
    (r'/',       web.HomeHandler),
    (r'/login',  web.LoginHandler),
    (r'/logout', web.LogoutHandler),
    
    (r'/user',   web.UserHandler),

    (r'/sync',   cli.SyncHandler),
    (r'/search', cli.SearchHandler),
    (r'/get',    cli.GetHandler),
]
