from ttfrog.db.base import Bases, BaseObject, IterableMixin

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint


__all__ = [
    'Skill',
    'Proficiency',
    'Modifier',
]


class Skill(*Bases):
    __tablename__ = "skill"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    description = Column(Text)

    def __repr__(self):
        return str(self.name)


class Proficiency(*Bases):
    __tablename__ = "proficiency"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)

    def __repr__(self):
        return str(self.name)


class Modifier(BaseObject, IterableMixin):
    __tablename__ = "modifier"
    __table_args__ = (
        UniqueConstraint('source_table_name', 'source_table_id', 'value', 'type', 'target'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_table_name = Column(String, index=True, nullable=False)
    source_table_id = Column(Integer, index=True, nullable=False)
    value = Column(String, nullable=False)
    type = Column(String, nullable=False)
    target = Column(String, nullable=False)
