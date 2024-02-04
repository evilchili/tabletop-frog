from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
# from sqlalchemy import PrimaryKeyConstraint
# from sqlalchemy import DateTime

from ttfrog.db.base import Bases


class Ancestry(*Bases):
    __tablename__ = "ancestry"

    name = Column(String, primary_key=True, unique=True)

    def __repr__(self):
        return str(self.name)


class Character(*Bases):
    __tablename__ = "character"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ancestry = Column(String, ForeignKey("ancestry.name"), nullable=False)
    name = Column(String(255), nullable=False)
    level = Column(Integer, nullable=False, info={'min': 1, 'max': 20})
    str = Column(Integer, info={'min': 0, 'max': 30})
    dex = Column(Integer, info={'min': 0, 'max': 30})
    con = Column(Integer, info={'min': 0, 'max': 30})
    int = Column(Integer, info={'min': 0, 'max': 30})
    wis = Column(Integer, info={'min': 0, 'max': 30})
    cha = Column(Integer, info={'min': 0, 'max': 30})
