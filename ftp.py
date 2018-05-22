
import aioftp
from aiohttp import web
import asyncio

from utils import parse_headers
from errors import FtpProxyError, ServerUnreachable, MissingMandatoryQueryParameter


class AioftpError(FtpProxyError):
    def __init__(self, ftp_error):
        self.message = '\n'.join([info.strip() for info in ftp_error.info])


FTP_TIMEOUT = 5


async def ping(request):
    """test FTP connection by sending a minimal LS command
    returns "pong" on success
    """
    host, port, login, password = parse_headers(request)
    try:
        async with aioftp.ClientSession(host, port, login, password, socket_timeout=FTP_TIMEOUT, path_timeout=FTP_TIMEOUT) as client:
            async for _ in client.list('/'):  # noqa
                # Iterate once if any result, only list command matters not the results
                break
            return web.json_response({'success': True})
    except (OSError, asyncio.TimeoutError, TimeoutError):
        raise ServerUnreachable
    except aioftp.errors.StatusCodeError as ftp_error:
        raise AioftpError(ftp_error)


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

    try:
        async with aioftp.ClientSession(host, port, login, password, socket_timeout=FTP_TIMEOUT, path_timeout=FTP_TIMEOUT) as client:
            async for path, info in client.list(root_path, recursive=recursive):
                if extension is None or path.suffix == extension:
                    files.append(str(path))
    except (OSError, asyncio.TimeoutError, TimeoutError):
        raise ServerUnreachable
    except aioftp.errors.StatusCodeError as ftp_error:
        raise AioftpError(ftp_error)

    return web.json_response(files)


async def download(request):
    host, port, login, password = parse_headers(request)

    path = request.query.get('path')
    if not path:
        raise MissingMandatoryQueryParameter('path')
    try:
        async with aioftp.ClientSession(host, port, login, password, socket_timeout=FTP_TIMEOUT, path_timeout=FTP_TIMEOUT) as client:
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
        raise AioftpError(ftp_error)
