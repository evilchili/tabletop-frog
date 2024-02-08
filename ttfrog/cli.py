import io
import logging
import os
from pathlib import Path
from typing import Optional
from textwrap import dedent

import typer
from dotenv import load_dotenv
from rich import print
from rich.logging import RichHandler

from ttfrog.path import assets


default_data_path = Path("~/.dnd/ttfrog")
default_host = '127.0.0.1'
default_port = 2323

SETUP_HELP = f"""
# Please make sure you set the SECRET_KEY in your environment. By default,
# TableTop Frog will attempt to load these variables from:
#     {default_data_path}/defaults
#
# which may contain the following variables as well.
#
# See also the --root paramter.

DATA_PATH={default_data_path}

# Uncomment one or both of these to replace the packaged static assets and templates:
#
# STATIC_FILES_PATH={assets()}/public
# TEMPLATES_PATH={assets()}/templates

HOST={default_host}
PORT={default_port}
"""

app = typer.Typer()
app_state = dict()


@app.callback()
def main(
    context: typer.Context,
    root: Optional[Path] = typer.Option(
        default_data_path,
        help="Path to the TableTop Frog environment",
    )
):
    app_state['env'] = root.expanduser() / Path('defaults')
    load_dotenv(stream=io.StringIO(SETUP_HELP))
    load_dotenv(app_state['env'])
    debug = os.getenv('DEBUG', None)
    logging.basicConfig(
        format='%(message)s',
        level=logging.DEBUG if debug else logging.INFO,
        handlers=[
            RichHandler(rich_tracebacks=True, tracebacks_suppress=[typer])
        ]
    )


@app.command()
def setup(context: typer.Context):
    """
    (Re)Initialize TableTop Frog. Idempotent; will preserve any existing configuration.
    """
    from ttfrog.db.bootstrap import bootstrap
    if not os.path.exists(app_state['env']):
        app_state['env'].parent.mkdir(parents=True, exist_ok=True)
        app_state['env'].write_text(dedent(SETUP_HELP))
        print(f"Wrote defaults file {app_state['env']}.")
    bootstrap()


@app.command()
def serve(
    context: typer.Context,
    host: str = typer.Argument(
        default_host,
        help="bind address",
    ),
    port: int = typer.Argument(
        default_port,
        help="bind port",
    ),
    debug: bool = typer.Option(
        False,
        help='Enable debugging output'
    ),
):
    """
    Start the TableTop Frog server.
    """

    # delay loading the app until we have configured our environment
    from ttfrog.webserver import application
    from ttfrog.db.bootstrap import bootstrap

    print("Starting TableTop Frog server...")
    bootstrap()
    application.start(host=host, port=port, debug=debug)


if __name__ == '__main__':
    app()
