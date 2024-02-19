from ttfrog.db.base import BaseObject, IterableMixin
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

__all__ = ['TransactionLog']

class TransactionLog(BaseObject, IterableMixin):
    __tablename__ = "transaction_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_table_name = Column(String, index=True, nullable=False)
    primary_key = Column(Integer, index=True)
    diff = Column(Text)
