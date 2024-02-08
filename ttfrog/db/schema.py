import enum

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Enum
from sqlalchemy import Text

from ttfrog.db.base import Bases, BaseObject, IterableMixin
from ttfrog.db.base import multivalue_string_factory


STATS = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']

CREATURE_TYPES = ['aberation', 'beast', 'celestial', 'construct', 'dragon', 'elemental', 'fey', 'fiend', 'Giant',
                  'humanoid', 'monstrosity', 'ooze', 'plant', 'undead']

# enums for db schemas
StatsEnum = enum.Enum("StatsEnum", ((k, k) for k in STATS))
CreatureTypesEnum = enum.Enum("CreatureTypesEnum", ((k, k) for k in CREATURE_TYPES))

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

    def __repr__(self):
        return str(self.name)


class CharacterClass(*Bases, SavingThrowsMixin, SkillsMixin):
    __tablename__ = "character_class"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    hit_dice = Column(String, default='1d6')
    hit_dice_stat = Column(Enum(StatsEnum))
    proficiencies = Column(String)

    def __repr__(self):
        return str(self.name)


class Character(*Bases, CharacterClassMixin, SavingThrowsMixin, SkillsMixin):
    __tablename__ = "character"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ancestry = Column(String, ForeignKey("ancestry.name"), nullable=False)
    name = Column(String(255), nullable=False)
    level = Column(Integer, nullable=False, info={'min': 1, 'max': 20})
    armor_class = Column(Integer, nullable=False, info={'min': 1, 'max': 99})
    hit_points = Column(Integer, nullable=False, info={'min': 0, 'max': 999})
    max_hit_points = Column(Integer, nullable=False, info={'min': 0, 'max': 999})
    temp_hit_points = Column(Integer, nullable=False, info={'min': 0})
    passive_perception = Column(Integer, nullable=False)
    passive_insight = Column(Integer, nullable=False)
    passive_investigation = Column(Integer, nullable=False)
    speed = Column(String, nullable=False, default="30 ft.")
    str = Column(Integer, info={'min': 0, 'max': 30})
    dex = Column(Integer, info={'min': 0, 'max': 30})
    con = Column(Integer, info={'min': 0, 'max': 30})
    int = Column(Integer, info={'min': 0, 'max': 30})
    wis = Column(Integer, info={'min': 0, 'max': 30})
    cha = Column(Integer, info={'min': 0, 'max': 30})
    proficiencies = Column(String)


class TransactionLog(BaseObject, IterableMixin):
    __tablename__ = "transaction_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_table_name = Column(String, index=True, nullable=False)
    primary_key = Column(Integer, index=True)
    diff = Column(Text)
