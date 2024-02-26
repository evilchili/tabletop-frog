from ttfrog.db.base import Bases, BaseObject, IterableMixin, SavingThrowsMixin, SkillsMixin
from ttfrog.db.base import StatsEnum

from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


__all__ = [
    'ClassAttributeMap',
    'ClassAttribute',
    'ClassAttributeOption',
    'CharacterClass',
]


class ClassAttributeMap(BaseObject, IterableMixin):
    __tablename__ = "class_attribute_map"
    class_attribute_id = Column(Integer, ForeignKey("class_attribute.id"), primary_key=True)
    character_class_id = Column(Integer, ForeignKey("character_class.id"), primary_key=True)
    level = Column(Integer, nullable=False, info={'min': 1, 'max': 20}, default=1)


class ClassAttribute(BaseObject, IterableMixin):
    __tablename__ = "class_attribute"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return f"{self.id}: {self.name}"


class ClassAttributeOption(BaseObject, IterableMixin):
    __tablename__ = "class_attribute_option"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    attribute_id = Column(Integer, ForeignKey("class_attribute.id"), nullable=False)
    # attribute = relationship("ClassAttribute", uselist=False)


class CharacterClass(*Bases, SavingThrowsMixin, SkillsMixin):
    __tablename__ = "character_class"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    hit_dice = Column(String, default='1d6')
    hit_dice_stat = Column(Enum(StatsEnum))
    proficiencies = Column(String)
    attributes = relationship("ClassAttributeMap")
