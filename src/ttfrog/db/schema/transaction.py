from sqlalchemy import Column, Integer, String, Text

from ttfrog.db.base import BaseObject, IterableMixin

__all__ = ["TransactionLog"]


class TransactionLog(BaseObject, IterableMixin):
    __tablename__ = "transaction_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_table_name = Column(String, index=True, nullable=False)
    primary_key = Column(Integer, index=True)
    diff = Column(Text)
