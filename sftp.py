
from aiohttp import web
import asyncssh

from utils import parse_headers, asyncio_timeout
from errors import FtpProxyError, ServerUnreachable, MissingMandatoryQueryParameter


SFTP_TIMEOUT = 5
CHUNK_SIZE = 8192


class AsyncsshError(FtpProxyError):
    def __init__(self, error):
        self.message = error.reason


@asyncio_timeout(SFTP_TIMEOUT)
async def ping(request):
    """test SFTP connection by sending a minimal LS command
    returns "pong" on success
    """
    host, port, username, password = parse_headers(request, default_user=None, default_port=22)

    try:
        # known_hosts explicitly disabled
        async with asyncssh.connect(host, port=port, username=username, password=password, known_hosts=None) as conn:
            async with conn.start_sftp_client():
                return web.json_response({'success': True})
    except asyncssh.misc.Error as exc:
        raise AsyncsshError(exc)
    except OSError:
        raise ServerUnreachable


@asyncio_timeout(SFTP_TIMEOUT)
async def ls(request):
    """
    :param path: (optional) Path to list
    :param extension: (optional) Filter by extension
    """
    host, port, username, password = parse_headers(request, default_user=None, default_port=22)
    path = request.query.get('path', '')
    path = path.rstrip('/') + '/'
    extension = request.query.get('extension', '')

    try:
        async with asyncssh.connect(host, port=port, username=username, password=password, known_hosts=None) as conn:
            async with conn.start_sftp_client() as sftp:
                files = [f'{path}{f}' for f in await sftp.listdir(path)
                         if f not in ('.', '..') and (not extension or f.endswith(extension))]
                return web.json_response(files)
    except asyncssh.misc.Error as exc:
        raise AsyncsshError(exc)
    except OSError:
        raise ServerUnreachable


@asyncio_timeout(SFTP_TIMEOUT)
async def download(request):
    """
    :param path: Filepath
    """
    host, port, username, password = parse_headers(request, default_user=None, default_port=22)
    path = request.query.get('path', '')
    if not path:
        raise MissingMandatoryQueryParameter('path')

    try:
        async with asyncssh.connect(host, port=port, username=username, password=password, known_hosts=None) as conn:
            async with conn.start_sftp_client() as sftp:
                async with sftp.open(path, 'rb') as fp:
                    response = web.StreamResponse()
                    response.content_type = 'application/octet-stream'
                    await response.prepare(request)

                    chunk = await fp.read(CHUNK_SIZE)
                    while chunk:
                        await response.write(chunk)
                        chunk = await fp.read(CHUNK_SIZE)

                    return response

    except asyncssh.misc.Error as exc:
        raise AsyncsshError(exc)
    except OSError:
        raise ServerUnreachable
