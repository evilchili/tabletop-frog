from collections import defaultdict

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ttfrog.db.base import BaseObject, Bases, IterableMixin, SavingThrowsMixin, SkillsMixin, StatsEnum

__all__ = [
    "ClassAttributeMap",
    "ClassAttribute",
    "ClassAttributeOption",
    "CharacterClass",
]


class ClassAttributeMap(BaseObject, IterableMixin):
    __tablename__ = "class_attribute_map"
    class_attribute_id = Column(Integer, ForeignKey("class_attribute.id"), primary_key=True)
    character_class_id = Column(Integer, ForeignKey("character_class.id"), primary_key=True)
    level = Column(Integer, nullable=False, info={"min": 1, "max": 20}, default=1)
    attribute = relationship("ClassAttribute", uselist=False, viewonly=True, lazy="immediate")


class ClassAttribute(BaseObject, IterableMixin):
    __tablename__ = "class_attribute"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    options = relationship("ClassAttributeOption", cascade="all,delete,delete-orphan", lazy="immediate")

    def __repr__(self):
        return f"{self.id}: {self.name}"


class ClassAttributeOption(BaseObject, IterableMixin):
    __tablename__ = "class_attribute_option"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    attribute_id = Column(Integer, ForeignKey("class_attribute.id"), nullable=False)


class CharacterClass(*Bases, SavingThrowsMixin, SkillsMixin):
    __tablename__ = "character_class"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    hit_dice = Column(String, default="1d6")
    hit_dice_stat = Column(Enum(StatsEnum))
    proficiencies = Column(String)
    attributes = relationship("ClassAttributeMap", cascade="all,delete,delete-orphan", lazy="immediate")

    @property
    def attributes_by_level(self):
        by_level = defaultdict(list)
        for mapping in self.attributes:
            by_level[mapping.level] = {mapping.attribute.name: mapping.attribute}
        return by_level
