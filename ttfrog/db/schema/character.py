import logging


from ttfrog.db.base import Bases, BaseObject, IterableMixin, SavingThrowsMixin, SkillsMixin
from ttfrog.db.base import CreatureTypesEnum

from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy


__all__ = [
    'Ancestry',
    'AncestryTrait',
    'AncestryTraitMap',
    'CharacterClassMap',
    'CharacterClassAttributeMap',
    'Character',
]

def class_map_creator(fields):
    if isinstance(fields, CharacterClassMap):
        return fields
    return CharacterClassMap(**fields)


class AncestryTraitMap(BaseObject):
    __tablename__ = "trait_map"
    ancestry_id = Column(Integer, ForeignKey("ancestry.id"), primary_key=True)
    ancestry_trait_id = Column(Integer, ForeignKey("ancestry_trait.id"), primary_key=True)
    trait = relationship("AncestryTrait", lazy='immediate')
    level = Column(Integer, nullable=False, info={'min': 1, 'max': 20})


class Ancestry(*Bases):
    """
    A character ancestry ("race"), which has zero or more AncestryTraits.
    """
    __tablename__ = "ancestry"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    creature_type = Column(Enum(CreatureTypesEnum))
    traits = relationship("AncestryTraitMap", lazy='immediate')

    def __repr__(self):
        return self.name


class AncestryTrait(BaseObject, IterableMixin):
    """
    A trait granted to a character via its Ancestry.
    """
    __tablename__ = "ancestry_trait"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)


class CharacterClassMap(BaseObject):
    __tablename__ = "class_map"
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("character.id"))
    character_class_id = Column(Integer, ForeignKey("character_class.id"))
    mapping = UniqueConstraint(character_id, character_class_id)

    character_class = relationship("CharacterClass", lazy='immediate')
    level = Column(Integer, nullable=False, info={'min': 1, 'max': 20}, default=1)


class CharacterClassAttributeMap(BaseObject):
    __tablename__ = "character_class_attribute_map"
    class_attribute_id = Column(Integer, ForeignKey("class_attribute.id"), primary_key=True)
    character_id = Column(Integer, ForeignKey("character.id"), primary_key=True)
    attribute = relationship("ClassAttribute", lazy='immediate')


class Character(*Bases, SavingThrowsMixin, SkillsMixin):
    __tablename__ = "character"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, default='New Character', nullable=False)
    armor_class = Column(Integer, default=10, nullable=False, info={'min': 1, 'max': 99})
    hit_points = Column(Integer, default=1, nullable=False, info={'min': 0, 'max': 999})
    max_hit_points = Column(Integer, default=1, nullable=False, info={'min': 0, 'max': 999})
    temp_hit_points = Column(Integer, default=0, nullable=False, info={'min': 0, 'max': 999})
    speed = Column(Integer, nullable=False, default=30, info={'min': 0, 'max': 99})
    str = Column(Integer, nullable=False, default=10, info={'min': 0, 'max': 30})
    dex = Column(Integer, nullable=False, default=10, info={'min': 0, 'max': 30})
    con = Column(Integer, nullable=False, default=10, info={'min': 0, 'max': 30})
    int = Column(Integer, nullable=False, default=10, info={'min': 0, 'max': 30})
    wis = Column(Integer, nullable=False, default=10, info={'min': 0, 'max': 30})
    cha = Column(Integer, nullable=False, default=10, info={'min': 0, 'max': 30})
    proficiencies = Column(String)

    class_map = relationship("CharacterClassMap", cascade='all,delete,delete-orphan')
    classes = association_proxy('class_map', 'id', creator=class_map_creator)

    attributes = relationship("CharacterClassAttributeMap")

    ancestry_id = Column(Integer, ForeignKey("ancestry.id"), nullable=False, default='1')
    ancestry = relationship("Ancestry", uselist=False)
