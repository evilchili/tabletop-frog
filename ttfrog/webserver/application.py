import logging

from wsgiref.simple_server import make_server
from pyramid.config import Configurator

from ttfrog.db.manager import db
from ttfrog.webserver.routes import routes


def configuration():
    config = Configurator(settings={
        'sqlalchemy.url': db.url,
    })
    config.include('pyramid_tm')
    config.include('pyramid_sqlalchemy')
    return config


def start(host: str, port: int, debug: bool = False) -> None:
    logging.debug(f"Configuring webserver with {host=}, {port=}, {debug=}")
    config = configuration()
    config.include(routes)
    config.scan('ttfrog.webserver.views')
    make_server(host, int(port), config.make_wsgi_app()).serve_forever()
