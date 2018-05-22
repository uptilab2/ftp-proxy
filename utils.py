
import functools

import asyncio

from errors import MissingHostHeader, InvalidPortHeader, MissingUserHeader, ServerUnreachable


def parse_headers(request, default_port=21, default_user='anonymous', default_password=''):
    """Parse generic authentication headers common to all routes"""
    host = request.headers.get('X-ftpproxy-host')
    if host is None:
        raise MissingHostHeader
    port = request.headers.get('X-ftpproxy-port', default_port)
    try:
        port = int(port)
    except ValueError:
        raise InvalidPortHeader

    user = request.headers.get('X-ftpproxy-user', default_user)
    if not user:
        raise MissingUserHeader

    password = request.headers.get('X-ftpproxy-password', default_password)
    return host, port, user, password


def asyncio_timeout(timeout):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            future = func(*args, **kwargs)
            try:
                # Shield inside a timeout
                return await asyncio.wait_for(future, timeout)
            except asyncio.TimeoutError:
                raise ServerUnreachable  # TODO change error message ftom FTP to SFTP
        return wrapper
    return decorator
