from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint
# from sqlalchemy import PrimaryKeyConstraint
# from sqlalchemy import DateTime

from ttfrog.db.base import Bases


class Ancestry(*Bases):
    __tablename__ = "ancestry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    slug = Column(String, index=True, unique=True)


class Character(*Bases):
    __tablename__ = "character"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, index=True, unique=True)
    ancestry = Column(String, ForeignKey("ancestry.name"), nullable=False)
    name = Column(String(255), nullable=False)
    level = Column(Integer, nullable=False, info={'min': 1, 'max': 20})
    str = Column(Integer, info={'min': 1})
    dex = Column(Integer, info={'min': 1})
    con = Column(Integer, info={'min': 1})
    int = Column(Integer, info={'min': 1})
    wis = Column(Integer, info={'min': 1})
    cha = Column(Integer, info={'min': 1})
