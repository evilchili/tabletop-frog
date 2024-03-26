import os
from pathlib import Path

_setup_hint = "You may be able to solve this error by running 'ttfrog setup' or specifying the --root parameter."


def database():
    path = Path(os.environ["DATA_PATH"]).expanduser()
    if not path.exists() or not path.is_dir():
        raise RuntimeError(f"DATA_PATH {path} doesn't exist or isn't a directory.\n\n{_setup_hint}")
    return path / Path("tabletop-frog.db")


def assets():
    return Path(__file__).parent / "assets"


def templates():
    try:
        return Path(os.environ["TEMPLATES_PATH"])
    except KeyError:
        return assets() / "templates"


def static_files():
    try:
        return Path(os.environ["STATIC_FILES_PATH"])
    except KeyError:
        return assets() / "public"
