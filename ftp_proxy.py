
from aiohttp import web

from ftp import ftp_ping
from errors import FtpProxyError


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except FtpProxyError as error:
        return web.json_response({'error': error.message}, status=400)

def init_func(argv):
    app = web.Application()

    # Setup routes
    app.add_routes([web.get('/ftp/ping', ftp_ping)])

    # Setup middleware
    app.middlewares.append(error_middleware)

    return app
