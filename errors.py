
from aiohttp import web


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except FtpProxyError as error:
        return web.json_response({'error': error.message}, status=400)


class FtpProxyError(Exception):
    """Base exception class caught for every route"""
    pass


class MissingHostHeader(FtpProxyError):
    message = 'Missing mandatory X-ftpproxy-host header'


class MissingUserHeader(FtpProxyError):
    message = 'Missing mandatory X-ftpproxy-user header'


class InvalidPortHeader(FtpProxyError):
    message = 'Invalid X-ftpproxy-port header'


class ServerUnreachable(FtpProxyError):
    message = 'Failed connecting to FTP server'


class MissingMandatoryQueryParameter(FtpProxyError):
    def __init__(self, param_name):
        self.message = f'Missing mandatory query parameter: {param_name}'
