
import pytest

from ftp_proxy import init_func


@pytest.fixture
def client(aiohttp_client, loop):
    """Application client fixture"""
    app = init_func()
    return loop.run_until_complete(aiohttp_client(app))
