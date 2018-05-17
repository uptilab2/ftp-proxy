
from aiohttp import web


class FtpProxyError(Exception):
    """Base exception class caught for every route"""
    pass


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except FtpProxyError as error:
        return web.json_response({'error': error.message}, status=400)
