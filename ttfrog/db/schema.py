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

metadata = MetaData()

Ancestry = Table(
    "ancestry",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, index=True, unique=True),
    Column("slug", String, index=True, unique=True),
    Column("description", UnicodeText),
)

Character = Table(
    "character",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("slug", String, index=True, unique=True),
    Column("ancestry_name", Integer, ForeignKey("ancestry.name")),
    Column("name", String),
    Column("level", Integer, CheckConstraint('level > 0 AND level <= 20')),
    Column("str", Integer, CheckConstraint('str >=0')),
    Column("dex", Integer, CheckConstraint('dex >=0')),
    Column("con", Integer, CheckConstraint('con >=0')),
    Column("int", Integer, CheckConstraint('int >=0')),
    Column("wis", Integer, CheckConstraint('wis >=0')),
    Column("cha", Integer, CheckConstraint('cha >=0')),
)
