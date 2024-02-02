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


class FormValidatorMixin:
    """
    Add form validation capabilities using the .info attributes of columns.
    """

    # column.info could contain any of these keywords. define the list of validators that should apply
    # whenever we encounter one such keyword.
    _validators_by_keyword = {
        'min': [validators.NumberRange],
        'max': [validators.NumberRange],
    }

    @classmethod
    def validate(cls, form):
        for name, column in cls.__mapper__.columns.items():
            if name not in form._fields:
                continue

            # step through the info keywords and create a deduped list of validator classes that
            # should apply to this form field. This prevents adding unnecessary copies of the same
            # validator when two or more keywords map to the same one.
            extras = set()
            for key in column.info.keys():
                for val in cls._validators_by_keyword.get(key, []):
                    extras.add(val)

            # Add an instance of every unique validator for this column to the associated form field.
            form._fields[name].validators.extend([v(**column.info) for v in extras])

        # return the results of the form validation,.
        return form.validate()


# class Table(*Bases):
Bases = [BaseObject, IterableMixin, FormValidatorMixin, SlugMixin]
