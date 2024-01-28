import logging

from tg import MinimalApplicationConfigurator
from tg.configurator.components.statics import StaticsConfigurationComponent
from tg.configurator.components.sqlalchemy import SQLAlchemyConfigurationComponent
from tg.util.bunch import Bunch

from wsgiref.simple_server import make_server
import webhelpers2

from ttfrog.webserver import controllers
from ttfrog.db import db
import ttfrog.path


def app_globals():
    return Bunch


def application():
    """
    Create a TurboGears2 application
    """

    config = MinimalApplicationConfigurator()
    config.register(StaticsConfigurationComponent)
    config.register(SQLAlchemyConfigurationComponent)
    config.update_blueprint({

        # rendering
        'root_controller': controllers.RootController(),
        'default_renderer': 'jinja',
        'renderers': ['jinja'],
        'tg.jinja_filters': {},
        'auto_reload_templates': True,

        # helpers
        'app_globals': app_globals,
        'helpers': webhelpers2,
        'tw2.enabled': True,

        # assets
        'serve_static': True,
        'paths': {
            'static_files': ttfrog.path.static_files(),
            'templates': [ttfrog.path.templates()],
        },

        # db
        'use_sqlalchemy': True,
        'sqlalchemy.url': db.url,
        'model': db,
    })
    return config.make_wsgi_app()


def start(host: str, port: int, debug: bool = False) -> None:
    logging.debug(f"Configuring webserver with {host=}, {port=}, {debug=}")
    make_server(host, int(port), application()).serve_forever()
