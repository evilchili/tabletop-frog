import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ttfrog.db import schema
from ttfrog.db.manager import db as _db

FIXTURE_PATH = Path(__file__).parent / "fixtures"


def load_fixture(db, fixture_name):
    with db.transaction():
        data = json.loads((FIXTURE_PATH / f"{fixture_name}.json").read_text())
        for schema_name in data:
            for record in data[schema_name]:
                print(f"Loading {schema_name} {record = }")
                obj = getattr(schema, schema_name)(**record)
                db.session.add(obj)


@pytest.fixture(autouse=True)
def db(monkeypatch):
    monkeypatch.setattr("ttfrog.db.manager.database", MagicMock(return_value=""))
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("DEBUG", "1")
    _db.init()
    return _db


@pytest.fixture
def classes_factory(db):
    load_fixture(db, "classes")

    def factory():
        return dict((rec.name, rec) for rec in db.session.query(schema.CharacterClass).all())

    return factory


@pytest.fixture
def ancestries_factory(db):
    load_fixture(db, "ancestry")

    def factory():
        return dict((rec.name, rec) for rec in db.session.query(schema.Ancestry).all())

    return factory
