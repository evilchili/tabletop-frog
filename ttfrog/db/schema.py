from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UnicodeText
from sqlalchemy import ForeignKey
# from sqlalchemy import PrimaryKeyConstraint
# from sqlalchemy import DateTime


metadata = MetaData()

Ancestry = Table(
    "ancestry",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("slug", String, index=True, unique=True),
    Column("name", String, index=True, unique=True),
    Column("description", UnicodeText),
)

Character = Table(
    "character",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("slug", String, index=True, unique=True),
    Column("name", String),
    Column("ancestry_id", Integer, ForeignKey("ancestry.id")),
)
