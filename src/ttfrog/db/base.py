import enum

import nanoid
from nanoid_dictionary import human_alphabet
from pyramid_sqlalchemy import BaseObject as _BaseObject
from slugify import slugify
from sqlalchemy import Column, String


def genslug():
    return nanoid.generate(human_alphabet[2:], 5)


class SlugMixin:
    slug = Column(String, index=True, unique=True, default=genslug)

    @property
    def uri(self):
        return "-".join([self.slug, slugify(self.name.title().replace(" ", ""), ok="", only_ascii=True, lower=False)])


class BaseObject(_BaseObject):
    """
    Allows for iterating over Model objects' column names and values
    """
    __abstract__ = True

    def __iter__(self):
        values = vars(self)
        for attr in self.__mapper__.columns.keys():
            if attr in values:
                yield attr, values[attr]
        for relname in self.__mapper__.relationships.keys():
            relvals = []
            reliter = self.__getattribute__(relname)
            if not reliter:
                yield relname, relvals
                continue
            for rel in reliter:
                try:
                    relvals.append({k: v for k, v in vars(rel).items() if not k.startswith("_")})
                except TypeError:
                    relvals.append(rel)
            yield relname, relvals

    def __json__(self):
        """
        Provide a custom JSON encoder.
        """
        raise NotImplementedError()

    def __repr__(self):
        return str(dict(self))


def multivalue_string_factory(name, column=Column(String), separator=";"):
    """
    Generate a mixin class that adds a string column with getters and setters
    that convert list values to strings and back again. Equivalent to:

        class MultiValueString:
            _name = column

            @property
            def name_property(self):
                return self._name.split(';')

            @name.setter
            def name(self, val):
                return ';'.join(val)
    """
    attr = f"_{name}"
    prop = property(lambda self: getattr(self, attr).split(separator))
    setter = prop.setter(lambda self, val: setattr(self, attr, separator.join(val)))
    return type(
        "MultiValueString",
        (object,),
        {
            attr: column,
            f"{name}_property": prop,
            name: setter,
        },
    )


class EnumField(enum.Enum):
    """
    A serializable enum.
    """

    def __json__(self):
        return self.value


SavingThrowsMixin = multivalue_string_factory("saving_throws")
SkillsMixin = multivalue_string_factory("skills")

STATS = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
CREATURE_TYPES = [
    "aberation",
    "beast",
    "celestial",
    "construct",
    "dragon",
    "elemental",
    "fey",
    "fiend",
    "Giant",
    "humanoid",
    "monstrosity",
    "ooze",
    "plant",
    "undead",
]
CreatureTypesEnum = EnumField("CreatureTypesEnum", ((k, k) for k in CREATURE_TYPES))
StatsEnum = EnumField("StatsEnum", ((k, k) for k in STATS))
