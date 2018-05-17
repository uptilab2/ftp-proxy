
import aioftp
import pytest

from ftp_proxy import init_func


@pytest.fixture
def client(aiohttp_client, loop):
    """Application client fixture"""
    app = init_func()
    return loop.run_until_complete(aiohttp_client(app))


class FtpServer():
    """Provide testing ftp server as an async context manager"""
    def __init__(self, loop, host='localhost', port=2221, user=None, password=None):
        if user:
            users = aioftp.User(user, password),
            self.server = aioftp.Server(users, loop=loop)
        else:
            # Setup server with anonymous login
            self.server = aioftp.Server(loop=loop)
        self.host = host
        self.port = port

    async def __aenter__(self):
        await self.server.start(host=self.host, port=self.port)

    async def __aexit__(self, exc_type, exc, tb):
        await self.server.close()


class TestFtpPing:
    async def test_success(self, client, loop):
        async with FtpServer(loop, host='localhost', port=2221):
            headers = {
                'X-ftpproxy-host': 'localhost',
                'X-ftpproxy-port': '2221',
            }
            resp = await client.get('/ftp/ping', headers=headers)
            assert resp.status == 200

    async def test_unreachable_server(self, client, loop):
        headers = {
            'X-ftpproxy-host': 'localhost'
        }
        resp = await client.get('/ftp/ping', headers=headers)
        assert resp.status == 400
        assert await resp.json() == {'error': 'Failed connecting to FTP server'}

    async def test_mandatory_param(self, client):
        resp = await client.get('/ftp/ping')
        assert resp.status == 400
        assert await resp.json() == {'error': 'Missing mandatory X-ftpproxy-host header'}

    async def test_invalid_credentials(self, client, loop):
        async with FtpServer(loop, host='localhost', port=2221, user='someone'):
            headers = {
                'X-ftpproxy-host': 'localhost',
                'X-ftpproxy-port': '2221',
                'X-ftpproxy-user': 'roger',
            }
            resp = await client.get('/ftp/ping', headers=headers)
            assert resp.status == 400
            assert await resp.json() == {'error': [' no such username']}
