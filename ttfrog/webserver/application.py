import logging

from tg import MinimalApplicationConfigurator
from tg.configurator.components.statics import StaticsConfigurationComponent
from tg.configurator.components.sqlalchemy import SQLAlchemyConfigurationComponent
from tg.util.bunch import Bunch

from wsgiref.simple_server import make_server
import webhelpers2
import tw2.core

from ttfrog.webserver.controllers.root import RootController
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
        'root_controller': RootController(),
        'default_renderer': 'jinja',
        'renderers': ['jinja'],
        'tg.jinja_filters': {},
        'auto_reload_templates': True,

        # helpers
        'app_globals': app_globals,
        'helpers': webhelpers2,
        'use_toscawidgets2': True,

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

    # wrap the core wsgi app in a ToscaWidgets2 app
    return tw2.core.make_middleware(config.make_wsgi_app(), default_engine='jinja')


def start(host: str, port: int, debug: bool = False) -> None:
    logging.debug(f"Configuring webserver with {host=}, {port=}, {debug=}")
    make_server(host, int(port), application()).serve_forever()
