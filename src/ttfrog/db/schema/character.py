from collections import defaultdict

from sqlalchemy import Column, Enum, ForeignKey, Integer, Float, String, Text, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, validates

from ttfrog.db.base import BaseObject, CreatureTypesEnum, SavingThrowsMixin, SizesEnum, SkillsMixin, SlugMixin

__all__ = [
    "Ancestry",
    "AncestryTrait",
    "AncestryTraitMap",
    "AncestryModifier",
    "CharacterClassMap",
    "CharacterClassAttributeMap",
    "Character",
    "Modifier",
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
    __table_args__ = (UniqueConstraint("ancestry_id", "ancestry_trait_id"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    ancestry_id = Column(Integer, ForeignKey("ancestry.id"))
    ancestry_trait_id = Column(Integer, ForeignKey("ancestry_trait.id"))
    trait = relationship("AncestryTrait", lazy="immediate")
    level = Column(Integer, nullable=False, info={"min": 1, "max": 20})


# XXX: Replace this with a many-to-many on the Modifiers table. Will need for proficiecies too.
class Ancestry(BaseObject):
    """
    A character ancestry ("race"), which has zero or more AncestryTraits.
    """

    __tablename__ = "ancestry"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    creature_type = Column(Enum(CreatureTypesEnum), nullable=False, default="humanoid")
    size = Column(Enum(SizesEnum), nullable=False, default="Medium")
    speed = Column(Integer, nullable=False, default=30, info={"min": 0, "max": 99})
    _traits = relationship("AncestryTraitMap", lazy="immediate")
    modifiers = relationship("AncestryModifier", lazy="immediate")

    @property
    def traits(self):
        return [mapping.trait for mapping in self._traits]

    def add_trait(self, trait, level=1):
        if trait not in self.traits:
            self._traits.append(AncestryTraitMap(ancestry_id=self.id, ancestry_trait_id=trait.id, level=level))
            return True
        return False

    def add_modifier(self, modifier):
        if modifier not in self.modifiers:
            self.modifiers.append(modifier)
            return True
        return False

    def __repr__(self):
        return self.name


class AncestryModifier(BaseObject):
    """
    A modifier granted to a character via its Ancestry.
    """

    __tablename__ = "ancestry_modifier"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ancestry_id = Column(Integer, ForeignKey("ancestry.id"), nullable=False)
    name = Column(String, nullable=False)
    target = Column(String, nullable=False)
    absolute_value = Column(Integer)
    relative_value = Column(Integer)
    multiply_value = Column(Float)
    new_value = Column(String)
    description = Column(String, nullable=False)


class AncestryTrait(BaseObject):
    """
    A trait granted to a character via its Ancestry.
    """

    __tablename__ = "ancestry_trait"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)

    def __repr__(self):
        return self.name


class CharacterClassMap(BaseObject):
    __tablename__ = "class_map"
    __table_args__ = (UniqueConstraint("character_id", "character_class_id"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("character.id"), nullable=False)
    character_class_id = Column(Integer, ForeignKey("character_class.id"), nullable=False)
    level = Column(Integer, nullable=False, info={"min": 1, "max": 20}, default=1)

    character_class = relationship("CharacterClass", lazy="immediate")
    character = relationship("Character", uselist=False, viewonly=True)

    def __repr__(self):
        return "{self.character.name}, {self.character_class.name}, level {self.level}"


class CharacterClassAttributeMap(BaseObject):
    __tablename__ = "character_class_attribute_map"
    __table_args__ = (UniqueConstraint("character_id", "class_attribute_id"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("character.id"), nullable=False)
    class_attribute_id = Column(Integer, ForeignKey("class_attribute.id"), nullable=False)
    option_id = Column(Integer, ForeignKey("class_attribute_option.id"), nullable=False)

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


class Modifier(BaseObject):
    __tablename__ = "modifier"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("character.id"), nullable=False)
    target = Column(String, nullable=False)
    absolute_value = Column(Integer)
    relative_value = Column(Integer)
    multiply_value = Column(Float)
    new_value = Column(String)
    description = Column(String, nullable=False)


class Character(BaseObject, SlugMixin, SavingThrowsMixin, SkillsMixin):
    __tablename__ = "character"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, default="New Character", nullable=False)
    armor_class = Column(Integer, default=10, nullable=False, info={"min": 1, "max": 99})
    hit_points = Column(Integer, default=1, nullable=False, info={"min": 0, "max": 999})
    max_hit_points = Column(Integer, default=10, nullable=False, info={"min": 0, "max": 999})
    temp_hit_points = Column(Integer, default=0, nullable=False, info={"min": 0, "max": 999})
    strength = Column(Integer, nullable=False, default=10, info={"min": 0, "max": 30})
    dexterity = Column(Integer, nullable=False, default=10, info={"min": 0, "max": 30})
    constitution = Column(Integer, nullable=False, default=10, info={"min": 0, "max": 30})
    intelligence = Column(Integer, nullable=False, default=10, info={"min": 0, "max": 30})
    wisdom = Column(Integer, nullable=False, default=10, info={"min": 0, "max": 30})
    charisma = Column(Integer, nullable=False, default=10, info={"min": 0, "max": 30})
    proficiencies = Column(String)

    class_map = relationship("CharacterClassMap", cascade="all,delete,delete-orphan")
    class_list = association_proxy("class_map", "id", creator=class_map_creator)

    _modifiers = relationship("Modifier", cascade="all,delete,delete-orphan", lazy="immediate")
    _modify_ok = [
        "armor_class",
        "max_hit_points",
        "strength",
        "dexterity",
        "constitution",
        "intelligence",
        "wisdom",
        "charisma",
        "speed",
        "size",
    ]

    character_class_attribute_map = relationship("CharacterClassAttributeMap", cascade="all,delete,delete-orphan")
    attribute_list = association_proxy("character_class_attribute_map", "id", creator=attr_map_creator)

    ancestry_id = Column(Integer, ForeignKey("ancestry.id"), nullable=False, default="1")
    ancestry = relationship("Ancestry", uselist=False)

    @property
    def modifiers(self):
        all_modifiers = defaultdict(list)
        for mod in self.ancestry.modifiers:
            all_modifiers[mod.target].append(mod)
        for mod in self._modifiers:
            all_modifiers[mod.target].append(mod)
        return all_modifiers

    @property
    def classes(self):
        return dict([(mapping.character_class.name, mapping.character_class) for mapping in self.class_map])

    @property
    def traits(self):
        return self.ancestry.traits

    @property
    def AC(self):
        return self.apply_modifiers("armor_class", self.armor_class)

    @property
    def HP(self):
        return self.apply_modifiers("max_hit_points", self.max_hit_points)

    @property
    def STR(self):
        return self.apply_modifiers("strength", self.strength)

    @property
    def DEX(self):
        return self.apply_modifiers("dexterity", self.dexterity)

    @property
    def CON(self):
        return self.apply_modifiers("constitution", self.constitution)

    @property
    def INT(self):
        return self.apply_modifiers("intelligence", self.intelligence)

    @property
    def WIS(self):
        return self.apply_modifiers("wisdom", self.wisdom)

    @property
    def CHA(self):
        return self.apply_modifiers("charisma", self.charisma)

    @property
    def speed(self):
        return self.apply_modifiers("speed", self.ancestry.speed)

    @property
    def size(self):
        return self.apply_modifiers("size", self.ancestry.size)

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
            current_level = self.levels[thisclass.name]
            current_attributes = thisclass.attributes_by_level.get(current_level, {})
            if attribute.name in current_attributes:
                if attribute.name in self.class_attributes:
                    return True
                self.attribute_list.append(
                    CharacterClassAttributeMap(
                        character_id=self.id, class_attribute_id=attribute.id, option_id=option.id
                    )
                )
                return True
        return False


    def apply_modifiers(self, target, initial):
        modifiers = list(reversed(self.modifiers.get(target, [])))
        if isinstance(initial, int):
            absolute = [mod for mod in modifiers if mod.absolute_value is not None]
            if absolute:
                return absolute[0].absolute_value
            multiple = [mod for mod in modifiers if mod.multiply_value is not None]
            if multiple:
                return int(initial * multiple[0].multiply_value + 0.5)
            return initial + sum(mod.relative_value for mod in modifiers if mod.relative_value is not None)

        new = [mod for mod in modifiers if mod.new_value is not None]
        if new:
            return new[0].new_value
        return initial



    def add_modifier(self, modifier):
        if modifier.absolute_value is not None and modifier.relative_value is not None and modifier.multiple_value:
            raise AttributeError(f"You must provide only one of absolute, relative, and multiple values {modifier}.")
        self._modifiers.append(modifier)

    def remove_modifier(self, modifier):
        self._modifiers = [mod for mod in self._modifiers if mod != modifier]
