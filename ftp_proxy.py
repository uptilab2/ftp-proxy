
import argparse
from aiohttp import web

import ftp
import sftp
from errors import error_middleware


def init_func(argv=None):
    app = web.Application()

    # Setup routes
    app.add_routes([web.get('/ftp/ping', ftp.ping)])
    app.add_routes([web.get('/ftp/ls', ftp.ls)])
    app.add_routes([web.get('/ftp/download', ftp.download)])

    app.add_routes([web.get('/sftp/ping', sftp.ping)])
    app.add_routes([web.get('/sftp/ls', sftp.ls)])
    app.add_routes([web.get('/sftp/download', sftp.download)])

    # Setup middleware
    app.middlewares.append(error_middleware)

    return app


app = init_func()


def cli():
    parser = argparse.ArgumentParser(description="aiohttp server example")
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=2121, type=int)

    args = parser.parse_args()
    web.run_app(app, path=args.path, port=args.port)
