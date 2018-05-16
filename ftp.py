
import aioftp
from aiohttp import web
import asyncio

from errors import FtpProxyError


class MissingHostHeader(FtpProxyError):
    message = 'Missing mandatory X-ftpproxy-host header'


class ServerUnreachable(FtpProxyError):
    message = 'Failed connecting to FTP server'


class FtpError(FtpProxyError):
    def __init__(self, ftp_error):
        self.message = ftp_error.info


def parse_headers(request):
    host = request.headers.get('X-ftpproxy-host')
    if host is None:
        raise MissingHostHeader
    port = request.headers.get('X-ftpproxy-port', 21)
    user = request.headers.get('X-ftpproxy-user', 'anonymous')
    password = request.headers.get('X-ftpproxy-password', '')
    return host, port, user, password


async def ping(request):
    """test FTP connection by sending a minimal LS command
    returns "pong" on success
    """
    host, port, login, password = parse_headers(request)
    try:
        async with aioftp.ClientSession(host, port, login, password, socket_timeout=3, path_timeout=3) as client:
            async for _ in client.list('/'):
                # Iterate once if any result, only list command matters not the results
                break
            return web.Response(text='pong')
    except (OSError, asyncio.TimeoutError, TimeoutError):
        raise ServerUnreachable
    except aioftp.errors.StatusCodeError as ftp_error:
        raise FtpError(ftp_error)


async def ls(request):
    """ftp LS command

    Optional query params:
      path: directory to list (defaults to "/")
      recursive: recurse down folders (defaults to "false")
    """
    host, port, login, password = parse_headers(request)

    root_path = request.query.get('path', '/')
    recursive = request.query.get('recursive', 'false') == 'true'
    extension = request.query.get('extension')

    files = []
    directories = []

    try:
        async with aioftp.ClientSession(host, port, login, password, socket_timeout=3, path_timeout=3) as client:
            async for path, info in client.list(root_path, recursive=recursive):
                if info['type'] == 'dir' and extension is None:
                    directories.append(str(path))
                elif info['type'] == 'file':
                    if extension is None or path.suffix == extension:
                        files.append(str(path))
    except (OSError, asyncio.TimeoutError, TimeoutError):
        raise ServerUnreachable
    except aioftp.errors.StatusCodeError as ftp_error:
        raise FtpError(ftp_error)

    return web.json_response({'files': files, 'directories': directories})


async def download(request):
    host, port, login, password = parse_headers(request)

    path = request.query.get('path', '/')
    try:
        async with aioftp.ClientSession(host, port, login, password, socket_timeout=3, path_timeout=3) as client:
            ftp_stream = await client.download_stream(path)

            response = web.StreamResponse()
            response.content_type = 'application/octet-stream'
            await response.prepare(request)
            async for chunk in ftp_stream.iter_by_block():
                await response.write(chunk)
            return response
    except (OSError, asyncio.TimeoutError, TimeoutError):
        raise ServerUnreachable
    except aioftp.errors.StatusCodeError as ftp_error:
        raise FtpError(ftp_error)
