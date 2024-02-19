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
    'CharacterClass',
]


class ClassAttributeMap(BaseObject):
    __tablename__ = "class_attribute_map"
    class_attribute_id = Column(Integer, ForeignKey("class_attribute.id"), primary_key=True)
    character_class_id = Column(Integer, ForeignKey("character_class.id"), primary_key=True)
    attribute = relationship("ClassAttribute", lazy='immediate')
    level = Column(Integer, nullable=False, info={'min': 1, 'max': 20}, default=1)


class ClassAttribute(BaseObject, IterableMixin):
    __tablename__ = "class_attribute"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    description = Column(Text)


class CharacterClass(*Bases, SavingThrowsMixin, SkillsMixin):
    __tablename__ = "character_class"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    hit_dice = Column(String, default='1d6')
    hit_dice_stat = Column(Enum(StatsEnum))
    proficiencies = Column(String)
    attributes = relationship("ClassAttributeMap")
