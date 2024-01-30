import transaction
import base64
import hashlib
import logging

from functools import cached_property

from pyramid_sqlalchemy import Session
from pyramid_sqlalchemy import init_sqlalchemy
from pyramid_sqlalchemy import metadata as _metadata

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

from ttfrog.path import database
import ttfrog.db.schema

ttfrog.db.schema


class SQLDatabaseManager:
    """
    A context manager for working with sqllite database.
    """
    @cached_property
    def url(self):
        return f"sqlite:///{database()}"

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

    def query(self, *args, **kwargs):
        return self.session.query(*args, **kwargs)

    def execute(self, statement) -> tuple:
        logging.info(statement)
        result = None
        error = None
        try:
            with transaction.manager as tx:
                result = self.session.execute(statement)
                tx.commit()
        except IntegrityError as exc:
            logging.error(exc)
            error = "I AM ERROR."
        return result, error

    def insert(self, table, **kwargs) -> tuple:
        stmt = table.insert().values(**kwargs)
        return self.execute(stmt)

    def update(self, table, **kwargs):
        primary_key = kwargs.pop('id')
        stmt = table.update().values(**kwargs).where(table.columns.id == primary_key)
        return self.execute(stmt)

    def slugify(self, rec: dict) -> str:
        """
        Create a uniquish slug from a dictionary.
        """
        sha1bytes = hashlib.sha1(str(rec['id']).encode())
        return base64.urlsafe_b64encode(sha1bytes.digest()).decode("ascii")[:10]

    def init(self):
        init_sqlalchemy(self.engine)
        self.metadata.create_all(self.engine)

    def __getattr__(self, name: str):
        try:
            return self.tables[name]
        except KeyError:
            raise AttributeError(f"{self} does not contain the attribute '{name}'.")


db = SQLDatabaseManager()
