from collections import defaultdict

from sqlalchemy import Column, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from ttfrog.db.base import BaseObject


class ModifierMap(BaseObject):
    """
    Creates a many-to-many between Modifier and any model inheriting from the ModifierMixin.
    """

    __tablename__ = "modifier_map"
    __table_args__ = (UniqueConstraint("primary_table_name", "primary_table_id", "modifier_id"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    primary_table_name = Column(String, nullable=False)
    primary_table_id = Column(Integer, nullable=False)
    modifier_id = Column(Integer, ForeignKey("modifier.id"), nullable=False)
    modifier = relationship("Modifier", uselist=False, lazy="immediate")


class Modifier(BaseObject):
    """
    Modifiers modify the base value of an existing attribute on another table.

    Modifiers are applied by the Character class, but may be associated with any model via the
    ModifierMixIn model; refer to the Ancestry class for an example.
    """

    __tablename__ = "modifier"
    id = Column(Integer, primary_key=True, autoincrement=True)
    target = Column(String, nullable=False)
    absolute_value = Column(Integer)
    relative_value = Column(Integer)
    multiply_value = Column(Float)
    new_value = Column(String)
    name = Column(String, nullable=False)
    description = Column(String)


class ModifierMixin:
    """
    Add modifiers to an existing class.

    Attributes:
         modifier_map   - get/set a list of Modifier records associated with the parent
         modifiers      - read-only dict of lists of modifiers keyed on Modifier.target

    Methods:
        add_modifier     - Add a Modifier association to the modifier_map
        remove_modifier  - Remove a modifier association from the modifier_map

    Example:

        >>> class Item(BaseObject, ModifierMixin):
                id = Column(Integer, primary_key=True, autoincrement=True)
                name = Column(String, nullable=False)
        >>> dwarven_belt = Item(name="Dwarven Belt")
        >>> dwarven_belt.add_modifier(Modifier(name="STR+1", target="strength", relative_value=1))
        >>> dwarven_belt.modifiers
        {'strength': [Modifier(id=1, target='strength', name='STR+1', relative_value=1 ... ]}
    """

    @declared_attr
    def modifier_map(cls):
        return relationship(
            "ModifierMap",
            primaryjoin=f"ModifierMap.primary_table_id == foreign({cls.__name__}.id)",
            cascade="all,delete,delete-orphan",
            single_parent=True,
            uselist=True,
            lazy="immediate",
        )

    @property
    def modifiers(self):
        all_modifiers = defaultdict(list)
        for mapping in self.modifier_map:
            all_modifiers[mapping.modifier.target].append(mapping.modifier)
        return all_modifiers

    def add_modifier(self, modifier):
        if modifier.absolute_value is not None and modifier.relative_value is not None and modifier.multiple_value:
            raise AttributeError(f"You must provide only one of absolute, relative, and multiple values {modifier}.")
        if [mod for mod in self.modifier_map if mod.modifier == modifier]:
            return False
        self.modifier_map.append(
            ModifierMap(
                primary_table_name=self.__tablename__,
                primary_table_id=self.id,
                modifier=modifier,
            )
        )
        return True

    def remove_modifier(self, modifier):
        if modifier.id not in [mod.modifier_id for mod in self.modifier_map]:
            return False
        self.modifier_map = [mapping for mapping in self.modifier_map if mapping.modifier != modifier]
        return True
