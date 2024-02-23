import logging

from ttfrog.webserver.controllers.base import BaseController
from ttfrog.webserver.forms import DeferredSelectField
from ttfrog.webserver.forms import NullableDeferredSelectField
from ttfrog.db.schema import Character, Ancestry, CharacterClass, CharacterClassMap
from ttfrog.db.base import STATS
from ttfrog.db.manager import db

from wtforms_alchemy import ModelForm
from wtforms.fields import SubmitField, SelectField, SelectMultipleField, FieldList, FormField, HiddenField
from wtforms.widgets import Select, ListWidget
from wtforms import ValidationError

VALID_LEVELS = range(1, 21)


class MulticlassForm(ModelForm):
    id = HiddenField()
    character_class_id = NullableDeferredSelectField(
        'CharacterClass',
        model=CharacterClass,
        validate_choice=True,
        widget=Select(),
        coerce=int
    )
    level = SelectField(choices=VALID_LEVELS, default=1, coerce=int, validate_choice=True, widget=Select())

    def __init__(self, formdata=None, obj=None, prefix=None):
        """
        Populate the form field with a CharacterClassMap object by converting the object ID
        to an instance. This will ensure that the rendered field is populated with the current
        value of the class_map.
        """
        obj = db.query(CharacterClassMap).get(obj)
        super().__init__(formdata=formdata, obj=obj, prefix=prefix)


class CharacterForm(ModelForm):
    class Meta:
        model = Character
        exclude = ['slug']

    save = SubmitField()
    delete = SubmitField()
    ancestry_id = DeferredSelectField('Ancestry', model=Ancestry, default=1, validate_choice=True, widget=Select())
    classes = FieldList(FormField(MulticlassForm, widget=ListWidget()), min_entries=0)
    newclass = FormField(MulticlassForm, widget=ListWidget())
    saving_throws = SelectMultipleField('Saving Throws', validate_choice=True, choices=STATS)


class CharacterSheet(BaseController):
    model = CharacterForm.Meta.model
    model_form = CharacterForm

    @property
    def resources(self):
        return super().resources + [
            {'type': 'script', 'uri': 'js/character_sheet.js'},
        ]

    def populate_class_map(self, formdata):
        """
        Populate the record's class_map association_proxy with dictionaries of
        CharacterClassMap field data. The creator factory on the proxy will
        convert dictionary data to CharacterClassMap instances..
        """
        populated = []
        for field in formdata:
            class_map_id = field.pop('id')
            class_map_id = int(class_map_id) if class_map_id else 0
            logging.debug(f"{class_map_id = }, {field = }, {self.record.classes = }")
            if not field['character_class_id']:
                continue
            elif not class_map_id:
                populated.append(field)
            else:
                field['id'] = class_map_id
                populated.append(field)
        self.record.classes = populated

    def validate_multiclass_form(self):
        """
        Validate multiclass fields in form data.
        """
        err = ""
        total_level = 0
        for field in self.form.data['classes']:
            level = field.get('level', 0)
            total_level += level
            if level not in VALID_LEVELS:
                err = f"Multiclass form field {field = } level is outside possible range."
                break
            if self.record.id and field.get('character_id', None) != self.record.id:
                err = f"Multiclass form field {field = } does not match character ID {self.record.id}"
                break
        if total_level not in VALID_LEVELS:
            err = f"Total level for all multiclasses ({total_level}) is outside possible range."
        if err:
            logging.error(err)
            raise ValidationError(err)

    def validate(self):
        """
        Add custom validation of the multiclass form data to standard form validation.
        """
        super().validate()
        self.validate_multiclass_form()

    def populate(self):
        """
        Delete the multiclass form data before calling form.populate_obj() and use
        our own method for populating the fieldlist.
        """
        formdata = self.form.data['classes']
        formdata.append(self.form.data['newclass'])
        del self.form.classes
        del self.form.newclass
        super().populate()
        self.populate_class_map(formdata)
