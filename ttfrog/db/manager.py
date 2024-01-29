import base64
import hashlib
import logging

from functools import cached_property

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError

from ttfrog.path import database
from ttfrog.db.schema import metadata


class SQLDatabaseManager:
    """
    A context manager for working with sqllite database.
    """
    @cached_property
    def url(self):
        return f"sqlite:///{database()}"

    @cached_property
    def engine(self):
        return create_engine(self.url, future=True)

    @cached_property
    def DBSession(self):
        maker = sessionmaker(bind=self.engine, future=True, autoflush=True)
        return scoped_session(maker)

    @cached_property
    def tables(self):
        return dict((t.name, t) for t in metadata.sorted_tables)

    def query(self, *args, **kwargs):
        return self.DBSession.query(*args, **kwargs)

    def execute(self, statement) -> tuple:
        logging.debug(statement)
        result = None
        error = None
        try:
            result = self.DBSession.execute(statement)
            self.DBSession.commit()
        except IntegrityError as exc:
            logging.error(exc)
            error = "An error occurred when saving changes."
        return result, error

    def insert(self, table, **kwargs) -> tuple:
        stmt = table.insert().values(**kwargs)
        return self.execute(stmt)

    def update(self, table, **kwargs):
        primary_key = kwargs.pop('id')
        stmt = table.update().values(**kwargs).where(table.columns.id == primary_key)
        return self.execute(stmt)

    def init_model(self, engine=None):
        metadata.create_all(bind=engine or self.engine)
        return self.DBSession

    def slugify(self, rec: dict) -> str:
        """
        Create a uniquish slug from a dictionary.
        """
        sha1bytes = hashlib.sha1(str(rec['id']).encode())
        return base64.urlsafe_b64encode(sha1bytes.digest()).decode("ascii")[:10]


    def __getattr__(self, name: str):
        try:
            return self.tables[name]
        except KeyError:
            raise AttributeError(f"{self} does not contain the attribute '{name}'.")

    def __enter__(self):
        self.init_model(self.engine)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.DBSession:
            self.DBSession.close()


db = SQLDatabaseManager()
session = db.DBSession
