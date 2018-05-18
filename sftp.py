
from aiohttp import web
import asyncio

from errors import FtpProxyError, MissingHostHeader, ServerUnreachable, MissingMandatoryQueryParameter


SFTP_TIMEOUT = 5


#class AioftpError(FtpProxyError):
#    def __init__(self, ftp_error):
#        self.message = '\n'.join([info.strip() for info in ftp_error.info])


#FTP_TIMEOUT = 5


def parse_headers(request):
    """Parse generic authentication headers common to all routes"""
    host = request.headers.get('X-ftpproxy-host')
    if host is None:
        raise MissingHostHeader
    port = request.headers.get('X-ftpproxy-port', 21)
    user = request.headers.get('X-ftpproxy-user', 'anonymous')
    password = request.headers.get('X-ftpproxy-password', '')
    return host, port, user, password


async def ping(request):
    future = _ping(request)
    try:
        # Shield inside a timeout
        return await asyncio.wait_for(future, SFTP_TIMEOUT)
    except asyncio.TimeoutError:
        raise ServerUnreachable  # TODO change error message ftom FTP to SFTP

async def _ping(request):
    """test SFTP connection by sending a minimal LS command
    returns "pong" on success
    """
    import asyncssh
    host = 'test.rebex.net'
    username = 'demo'
    password = 'password'
    # port = 21

    async with asyncssh.connect(host, username=username, password=password) as conn:
        async with conn.start_sftp_client() as sftp:
            return web.json_response({'success': True})
            files = await sftp.listdir('/')
            return web.json_response(files)
