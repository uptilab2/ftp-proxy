
import aioftp
from aiohttp import web
import asyncio

from errors import FtpProxyError


class MissingHostHeader(FtpProxyError):
    message = 'Missing mandatory X-ftpproxy-host header'


class ServerUnreachable(FtpProxyError):
    message = 'Failed connecting to FTP server'


def parse_headers(request):
    host = request.headers.get('X-ftpproxy-host')
    if host is None:
        raise MissingHostHeader
    port = request.headers.get('X-ftpproxy-port', 21)
    user = request.headers.get('X-ftpproxy-user', 'anonymous')
    password = request.headers.get('X-ftpproxy-password', '')
    return host, port, user, password


async def ftp_ping(request):

    host, port, login, password = parse_headers(request)

    try:
        async with aioftp.ClientSession(host, port, login, password, socket_timeout=3, path_timeout=3) as client:
            await client.list('/')
    except (asyncio.TimeoutError, TimeoutError):
        raise ServerUnreachable
    aioftp.errors.StatusCodeError
    # EXCEPTION aioftp.errors.StatusCodeError

    return web.Response(text='pong')
