
import aioftp


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
            assert await resp.json() == {'error': 'no such username'}


class TestFtpLs:
    async def test_default(self, client, loop):
        async with FtpServer(loop, host='localhost', port=2221):
            headers = {'X-ftpproxy-host': 'localhost', 'X-ftpproxy-port': '2221'}

            resp = await client.get('/ftp/ls', headers=headers)
            response_data = await resp.json()

            assert resp.status == 200
            assert '/README.md' in response_data['files']
            assert '/ftp_proxy.py' in response_data['files']
            assert '/tests' in response_data['directories']
            assert '/tests/integration_test.py' not in response_data['directories']

    async def test_path(self, client, loop):
        async with FtpServer(loop, host='localhost', port=2221):
            headers = {'X-ftpproxy-host': 'localhost', 'X-ftpproxy-port': '2221'}
            params = {'path': '/tests'}

            resp = await client.get('/ftp/ls', headers=headers, params=params)
            response_data = await resp.json()

            assert resp.status == 200
            assert response_data['directories'] == []
            assert response_data['files'] == ['/tests/integration_test.py']

    async def test_recursive(self, client, loop):
        async with FtpServer(loop, host='localhost', port=2221):
            headers = {'X-ftpproxy-host': 'localhost', 'X-ftpproxy-port': '2221'}
            params = {'recursive': 'true'}

            resp = await client.get('/ftp/ls', headers=headers, params=params)
            response_data = await resp.json()

            assert resp.status == 200
            assert '/README.md' in response_data['files']
            assert '/ftp_proxy.py' in response_data['files']
            assert '/tests/integration_test.py' in response_data['files']
            assert '/tests' in response_data['directories']

    async def test_extension(self, client, loop):
        async with FtpServer(loop, host='localhost', port=2221):
            headers = {'X-ftpproxy-host': 'localhost', 'X-ftpproxy-port': '2221'}
            params = {'recursive': 'true', 'extension': '.py'}

            resp = await client.get('/ftp/ls', headers=headers, params=params)
            response_data = await resp.json()

            assert resp.status == 200
            assert '/README.md' not in response_data['files']
            assert '/ftp_proxy.py' in response_data['files']
            assert '/tests/integration_test.py' in response_data['files']
            assert response_data['directories'] == []


class TestFtpDownload:
    async def test_default(self, client, loop):
        async with FtpServer(loop, host='localhost', port=2221):
            headers = {'X-ftpproxy-host': 'localhost', 'X-ftpproxy-port': '2221'}
            params = {'path': '/tests/integration_test.py'}

            resp = await client.get('/ftp/download', headers=headers, params=params)
            file_content = await resp.content.read()

            assert resp.status == 200
            assert resp.content_type == 'application/octet-stream'
            assert b'class TestFtpDownload:' in file_content

    async def test_mandatory_path(self, client, loop):
        async with FtpServer(loop, host='localhost', port=2221):
            headers = {'X-ftpproxy-host': 'localhost', 'X-ftpproxy-port': '2221'}

            resp = await client.get('/ftp/download', headers=headers)

            assert resp.status == 400
            assert await resp.json() == {'error': 'Missing mandatory query parameter: path'}

    async def test_invalid_path(self, client, loop):
        async with FtpServer(loop, host='localhost', port=2221):
            headers = {'X-ftpproxy-host': 'localhost', 'X-ftpproxy-port': '2221'}
            params = {'path': '/foo'}

            resp = await client.get('/ftp/download', headers=headers, params=params)

            assert resp.status == 400
            assert await resp.json() == {'error': 'path does not exists'}
