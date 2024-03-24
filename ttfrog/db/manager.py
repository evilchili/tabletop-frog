import os
import transaction
import base64
import hashlib

from contextlib import contextmanager
from functools import cached_property

from pyramid_sqlalchemy import Session
from pyramid_sqlalchemy import init_sqlalchemy
from pyramid_sqlalchemy import metadata as _metadata

from sqlalchemy import create_engine
# from sqlalchemy.exc import IntegrityError

from ttfrog.path import database
import ttfrog.db.schema

ttfrog.db.schema


class SQLDatabaseManager:
    """
    A context manager for working with sqllite database.
    """
    @cached_property
    def url(self):
        return os.environ.get('DATABASE_URL', f"sqlite:///{database()}")

    @cached_property
    def engine(self):
        return create_engine(self.url)

    @cached_property
    def session(self):
        return Session

    @cached_property
    def metadata(self):
        return _metadata

    @cached_property
    def tables(self):
        return dict((t.name, t) for t in self.metadata.sorted_tables)

    @contextmanager
    def transaction(self):
        with transaction.manager as tm:
            yield tm
            try:
                tm.commit()
            except Exception:
                tm.abort()
                raise

    def add(self, *args, **kwargs):
        self.session.add(*args, **kwargs)
        self.session.flush()

    def query(self, *args, **kwargs):
        return self.session.query(*args, **kwargs)

    def slugify(self, rec: dict) -> str:
        """
        Create a uniquish slug from a dictionary.
        """
        sha1bytes = hashlib.sha1(str(rec['id']).encode())
        return base64.urlsafe_b64encode(sha1bytes.digest()).decode("ascii")[:10]

    def init(self):
        init_sqlalchemy(self.engine)
        self.metadata.create_all(self.engine)

    def dump(self):
        results = {}
        for (table_name, table) in self.tables.items():
            results[table_name] = [row for row in self.query(table).all()]
        return results

    def __getattr__(self, name: str):
        try:
            return self.tables[name]
        except KeyError:
            raise AttributeError(f"{self} does not contain the attribute '{name}'.")


db = SQLDatabaseManager()
