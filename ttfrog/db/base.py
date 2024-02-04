import nanoid
from nanoid_dictionary import human_alphabet

from pyramid_sqlalchemy import BaseObject
from wtforms import validators
from slugify import slugify

from sqlalchemy import Column
from sqlalchemy import String


def genslug():
    return nanoid.generate(human_alphabet[2:], 5)


class SlugMixin:
    slug = Column(String, index=True, unique=True, default=genslug)

    @property
    def uri(self):
        return '-'.join([
            self.slug,
            slugify(self.name.title().replace(' ', ''), ok='', only_ascii=True, lower=False)
        ])


class IterableMixin:
    """
    Allows for iterating over Model objects' column names and values
    """
    def __iter__(self):
        values = vars(self)
        for attr in self.__mapper__.columns.keys():
            if attr in values:
                yield attr, values[attr]

    def __repr__(self):
        return f"{self.__class__.__name__}: {str(dict(self))}"


# class Table(*Bases):
Bases = [BaseObject, IterableMixin, SlugMixin]
