from sqlalchemy import Column, Integer, String, Text

from ttfrog.db.base import BaseObject

__all__ = [
    "Skill",
    "Proficiency",
]


class Skill(BaseObject):
    __tablename__ = "skill"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    description = Column(Text)

    def __repr__(self):
        return str(self.name)


class Proficiency(BaseObject):
    __tablename__ = "proficiency"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)

    def __repr__(self):
        return str(self.name)
