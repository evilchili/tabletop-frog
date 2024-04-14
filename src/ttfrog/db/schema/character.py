from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from ttfrog.db.base import BaseObject, Bases, CreatureTypesEnum, IterableMixin, SavingThrowsMixin, SkillsMixin

__all__ = [
    "Ancestry",
    "AncestryTrait",
    "AncestryTraitMap",
    "CharacterClassMap",
    "CharacterClassAttributeMap",
    "Character",
]


def class_map_creator(fields):
    if isinstance(fields, CharacterClassMap):
        return fields
    return CharacterClassMap(**fields)


def attr_map_creator(fields):
    if isinstance(fields, CharacterClassAttributeMap):
        return fields
    return CharacterClassAttributeMap(**fields)


class AncestryTraitMap(BaseObject):
    __tablename__ = "trait_map"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ancestry_id = Column(Integer, ForeignKey("ancestry.id"))
    ancestry_trait_id = Column(Integer, ForeignKey("ancestry_trait.id"))
    trait = relationship("AncestryTrait", lazy="immediate")
    level = Column(Integer, nullable=False, info={"min": 1, "max": 20})


class Ancestry(*Bases):
    """
    A character ancestry ("race"), which has zero or more AncestryTraits.
    """

    __tablename__ = "ancestry"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    creature_type = Column(Enum(CreatureTypesEnum))
    traits = relationship("AncestryTraitMap", lazy="immediate")

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

    def __repr__(self):
        return self.name


class CharacterClassMap(BaseObject, IterableMixin):
    __tablename__ = "class_map"
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("character.id"), nullable=False)
    character_class_id = Column(Integer, ForeignKey("character_class.id"), nullable=False)
    mapping = UniqueConstraint(character_id, character_class_id)
    level = Column(Integer, nullable=False, info={"min": 1, "max": 20}, default=1)

    character_class = relationship("CharacterClass", lazy="immediate")
    character = relationship("Character", uselist=False, viewonly=True)

    def __repr__(self):
        return "{self.character.name}, {self.character_class.name}, level {self.level}"


class CharacterClassAttributeMap(BaseObject, IterableMixin):
    __tablename__ = "character_class_attribute_map"
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("character.id"), nullable=False)
    class_attribute_id = Column(Integer, ForeignKey("class_attribute.id"), nullable=False)
    option_id = Column(Integer, ForeignKey("class_attribute_option.id"), nullable=False)
    mapping = UniqueConstraint(character_id, class_attribute_id)

    class_attribute = relationship("ClassAttribute", lazy="immediate")
    option = relationship("ClassAttributeOption", lazy="immediate")

    character_class = relationship(
        "CharacterClass",
        secondary="class_map",
        primaryjoin="CharacterClassAttributeMap.character_id == CharacterClassMap.character_id",
        secondaryjoin="CharacterClass.id == CharacterClassMap.character_class_id",
        viewonly=True,
        uselist=False,
    )


class Character(*Bases, SavingThrowsMixin, SkillsMixin):
    __tablename__ = "character"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, default="New Character", nullable=False)
    armor_class = Column(Integer, default=10, nullable=False, info={"min": 1, "max": 99})
    hit_points = Column(Integer, default=1, nullable=False, info={"min": 0, "max": 999})
    max_hit_points = Column(Integer, default=1, nullable=False, info={"min": 0, "max": 999})
    temp_hit_points = Column(Integer, default=0, nullable=False, info={"min": 0, "max": 999})
    speed = Column(Integer, nullable=False, default=30, info={"min": 0, "max": 99})
    str = Column(Integer, nullable=False, default=10, info={"min": 0, "max": 30})
    dex = Column(Integer, nullable=False, default=10, info={"min": 0, "max": 30})
    con = Column(Integer, nullable=False, default=10, info={"min": 0, "max": 30})
    int = Column(Integer, nullable=False, default=10, info={"min": 0, "max": 30})
    wis = Column(Integer, nullable=False, default=10, info={"min": 0, "max": 30})
    cha = Column(Integer, nullable=False, default=10, info={"min": 0, "max": 30})
    proficiencies = Column(String)

    class_map = relationship("CharacterClassMap", cascade="all,delete,delete-orphan")
    class_list = association_proxy("class_map", "id", creator=class_map_creator)

    character_class_attribute_map = relationship("CharacterClassAttributeMap", cascade="all,delete,delete-orphan")
    attribute_list = association_proxy("character_class_attribute_map", "id", creator=attr_map_creator)

    ancestry_id = Column(Integer, ForeignKey("ancestry.id"), nullable=False, default="1")
    ancestry = relationship("Ancestry", uselist=False)

    @property
    def classes(self):
        return dict([(mapping.character_class.name, mapping.character_class) for mapping in self.class_map])

    @property
    def traits(self):
        return [mapping.trait for mapping in self.ancestry.traits]

    @property
    def level(self):
        return sum(mapping.level for mapping in self.class_map)

    @property
    def levels(self):
        return dict([(mapping.character_class.name, mapping.level) for mapping in self.class_map])

    @property
    def class_attributes(self):
        return dict([(mapping.class_attribute.name, mapping.option) for mapping in self.character_class_attribute_map])

    def add_class(self, newclass, level=1):
        if level == 0:
            return self.remove_class(newclass)
        level_in_class = [mapping for mapping in self.class_map if mapping.character_class_id == newclass.id]
        if level_in_class:
            level_in_class = level_in_class[0]
            level_in_class.level = level
        else:
            self.class_list.append(CharacterClassMap(character_id=self.id, character_class_id=newclass.id, level=level))
        for lvl in range(1, level + 1):
            if not newclass.attributes_by_level[lvl]:
                continue
            for attr_name, attr in newclass.attributes_by_level[lvl].items():
                self.add_class_attribute(attr, attr.options[0])

    def remove_class(self, target):
        self.class_map = [m for m in self.class_map if m.id != target.id]
        for mapping in self.character_class_attribute_map:
            if mapping.character_class.id == target.id:
                self.remove_class_attribute(mapping.class_attribute)

    def remove_class_attribute(self, attribute):
        self.character_class_attribute_map = [m for m in self.character_class_attribute_map if m.id != attribute.id]

    def add_class_attribute(self, attribute, option):
        for thisclass in self.classes.values():
            # this test is failing?
            if attribute.name in thisclass.attributes_by_level.get(self.levels[thisclass.name], {}):
                self.attribute_list.append(
                    CharacterClassAttributeMap(
                        character_id=self.id, class_attribute_id=attribute.id, option_id=option.id
                    )
                )
                return True
        return False
