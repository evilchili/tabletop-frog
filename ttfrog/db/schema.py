import enum

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Enum
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from ttfrog.db.base import Bases, BaseObject, IterableMixin
from ttfrog.db.base import multivalue_string_factory


STATS = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']

CREATURE_TYPES = ['aberation', 'beast', 'celestial', 'construct', 'dragon', 'elemental', 'fey', 'fiend', 'Giant',
                  'humanoid', 'monstrosity', 'ooze', 'plant', 'undead']


class EnumField(enum.Enum):
    """
    A serializable enum.
    """
    def __json__(self, request):
        return self.value


# enums for db schemas
StatsEnum = EnumField("StatsEnum", ((k, k) for k in STATS))
CreatureTypesEnum = EnumField("CreatureTypesEnum", ((k, k) for k in CREATURE_TYPES))

CharacterClassMixin = multivalue_string_factory('character_class', Column(String, nullable=False))
SavingThrowsMixin = multivalue_string_factory('saving_throws')
SkillsMixin = multivalue_string_factory('skills')


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


class Ancestry(*Bases):
    __tablename__ = "ancestry"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    creature_type = Column(Enum(CreatureTypesEnum))
    traits = relationship("AncestryTrait")

    def __repr__(self):
        return str(self.name)


class AncestryTrait(BaseObject, IterableMixin):
    __tablename__ = "ancestry_trait"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ancestry_id = Column(Integer, ForeignKey("ancestry.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    level = Column(Integer, nullable=False, info={'min': 1, 'max': 20})


class CharacterClass(*Bases, SavingThrowsMixin, SkillsMixin):
    __tablename__ = "character_class"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    hit_dice = Column(String, default='1d6')
    hit_dice_stat = Column(Enum(StatsEnum))
    proficiencies = Column(String)

    def __repr__(self):
        return str(self.name)


class ClassAttribute(BaseObject, IterableMixin):
    __tablename__ = "class_attribute"
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_class_id = Column(Integer, ForeignKey("character_class.id"), nullable=False)
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    description = Column(Text)
    level = Column(Integer, nullable=False, info={'min': 1, 'max': 20})

    def __repr__(self):
        return str(self.name)


class Character(*Bases, CharacterClassMixin, SavingThrowsMixin, SkillsMixin):
    __tablename__ = "character"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ancestry = Column(String, ForeignKey("ancestry.name"), nullable=False, default='human')
    name = Column(String, default='New Character', nullable=False)
    level = Column(Integer, default=1, nullable=False, info={'min': 1, 'max': 20})
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


class TransactionLog(BaseObject, IterableMixin):
    __tablename__ = "transaction_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_table_name = Column(String, index=True, nullable=False)
    primary_key = Column(Integer, index=True)
    diff = Column(Text)
