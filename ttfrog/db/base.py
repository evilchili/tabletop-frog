import nanoid
from nanoid_dictionary import human_alphabet
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import String
from pyramid_sqlalchemy import BaseObject
from slugify import slugify


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


def multivalue_string_factory(name, column=Column(String), separator=';'):
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
    return type('MultiValueString', (object, ), {
        attr: column,
        f"{name}_property": prop,
        name: setter,
    })


# class Table(*Bases):
Bases = [BaseObject, IterableMixin, SlugMixin]
