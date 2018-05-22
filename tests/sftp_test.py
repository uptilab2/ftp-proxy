
import asyncssh


import pytest


class SFTPServer(asyncssh.SFTPServer):
    def __init__(self, conn):
        # Serve current folder instead of system root
        super().__init__(conn, '.')


class SSHServer(asyncssh.SSHServer):
    USERNAME = 'foo'
    PASSWORD = 'password'

    def begin_auth(self, username):
        # Mandatory authentication
        return True

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        return username == self.USERNAME and password == self.PASSWORD


@pytest.fixture(scope='session')
def host_key():
    return asyncssh.generate_private_key('ecdsa-sha2-nistp256')


@pytest.fixture()
def sftp_server(loop, host_key):
    server = asyncssh.create_server(SSHServer, host='', port=8022, loop=loop,
                                    sftp_factory=SFTPServer, server_host_keys=[host_key])
    loop.run_until_complete(server)


class TestFtpPing:
    async def test_invalid_login(self, client, sftp_server):
        headers = {
            'X-ftpproxy-host': 'localhost',
            'X-ftpproxy-port': '8022',
            'X-ftpproxy-user': 'unknown',
            'X-ftpproxy-password': 'credentials',
        }
        resp = await client.get('/sftp/ping', headers=headers)
        assert resp.status == 400, await resp.text()
        assert await resp.json() == {'error': 'Permission denied'}

    async def test_invalid_password(self, client, sftp_server):
        headers = {
            'X-ftpproxy-host': 'localhost',
            'X-ftpproxy-port': '8022',
            'X-ftpproxy-user': 'foo',
            'X-ftpproxy-password': 'invalid',
        }
        resp = await client.get('/sftp/ping', headers=headers)
        assert resp.status == 400
        assert await resp.json() == {'error': 'Permission denied'}

    async def test_invalid_host(self, client, sftp_server):
        headers = {
            'X-ftpproxy-host': 'localhost',
            'X-ftpproxy-port': '8404',
            'X-ftpproxy-user': 'foo',
            'X-ftpproxy-password': 'password',
        }
        resp = await client.get('/sftp/ping', headers=headers)
        assert resp.status == 400
        assert await resp.json() == {'error': 'Failed connecting to FTP server'}

    async def test_success(self, client, sftp_server):
        headers = {
            'X-ftpproxy-host': 'localhost',
            'X-ftpproxy-port': '8022',
            'X-ftpproxy-user': 'foo',
            'X-ftpproxy-password': 'password',
        }
        resp = await client.get('/sftp/ping', headers=headers)
        assert resp.status == 200


class TestSftpLs:
    async def test_default(self, client, sftp_server):
        headers = {
            'X-ftpproxy-host': 'localhost',
            'X-ftpproxy-port': '8022',
            'X-ftpproxy-user': 'foo',
            'X-ftpproxy-password': 'password',
        }

        resp = await client.get('/sftp/ls', headers=headers)
        assert resp.status == 200

        response_data = await resp.json()
        assert '/README.md' in response_data
        assert '/ftp_proxy.py' in response_data
        assert '/tests' in response_data
        assert '/tests/sft_test.py' not in response_data
