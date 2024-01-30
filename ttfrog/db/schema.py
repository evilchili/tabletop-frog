from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UnicodeText
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint
# from sqlalchemy import PrimaryKeyConstraint
# from sqlalchemy import DateTime

from pyramid_sqlalchemy import BaseObject

class Ancestry(BaseObject):
    __tablename__ = "ancestry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    slug = Column(String, index=True, unique=True)


class Character(BaseObject):
    __tablename__ = "character"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, index=True, unique=True)
    ancestry = Column(String, ForeignKey("ancestry.name"))
    name = Column(String)
    level = Column(Integer, CheckConstraint('level > 0 AND level <= 20'))
    str = Column(Integer, CheckConstraint('str >=0'))
    dex = Column(Integer, CheckConstraint('dex >=0'))
    con = Column(Integer, CheckConstraint('con >=0'))
    int = Column(Integer, CheckConstraint('int >=0'))
    wis = Column(Integer, CheckConstraint('wis >=0'))
    cha = Column(Integer, CheckConstraint('cha >=0'))
