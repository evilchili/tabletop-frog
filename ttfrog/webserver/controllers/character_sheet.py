import logging

from ttfrog.webserver.controllers.base import BaseController
from ttfrog.webserver.forms import DeferredSelectField
from ttfrog.webserver.forms import NullableDeferredSelectField
from ttfrog.db.schema import (
    Character,
    Ancestry,
    CharacterClass,
    CharacterClassMap,
    ClassAttributeOption,
    CharacterClassAttributeMap
)

from ttfrog.db.base import STATS
from ttfrog.db.manager import db

from wtforms_alchemy import ModelForm
from wtforms.fields import SubmitField, SelectField, SelectMultipleField, FieldList, FormField, HiddenField
from wtforms.widgets import Select, ListWidget
from wtforms import ValidationError
from wtforms.validators import Optional

VALID_LEVELS = range(1, 21)


class ClassAttributesForm(ModelForm):
    id = HiddenField()
    class_attribute_id = HiddenField()

    option_id = SelectField(
        widget=Select(),
        choices=[],
        validators=[Optional()],
        coerce=int
    )

    def __init__(self, formdata=None, obj=None, prefix=None):
        if obj:
            obj = db.query(CharacterClassAttributeMap).get(obj)
        super().__init__(formdata=formdata, obj=obj, prefix=prefix)

        if obj:
            options = db.query(ClassAttributeOption).filter_by(attribute_id=obj.class_attribute.id)
            self.option_id.label = obj.class_attribute.name
            self.option_id.choices = [(rec.id, rec.name) for rec in options.all()]


class MulticlassForm(ModelForm):

    id = HiddenField()
    character_class_id = NullableDeferredSelectField(
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
        if obj:
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

    class_attributes = FieldList(FormField(ClassAttributesForm, widget=ListWidget()), min_entries=1)

    saving_throws = SelectMultipleField('Saving Throws', validate_choice=True, choices=STATS)


class CharacterSheet(BaseController):
    model = CharacterForm.Meta.model
    model_form = CharacterForm

    @property
    def resources(self):
        return super().resources + [
            {'type': 'script', 'uri': 'js/character_sheet.js'},
        ]

    def validate_callback(self):
        """
        Validate multiclass fields in form data.
        """
        ret = super().validate()
        if not self.form.data['classes']:
            return ret

        err = ""
        total_level = 0
        for field in self.form.data['classes']:
            level = field.get('level')
            total_level += level
            if level not in VALID_LEVELS:
                err = f"Multiclass form field {field = } level is outside possible range."
                break
        if total_level not in VALID_LEVELS:
            err = f"Total level for all multiclasses ({total_level}) is outside possible range."
        if err:
            logging.error(err)
            raise ValidationError(err)
        return ret and True

    def add_class_attributes(self):
        # prefetch the records for each of the character's classes
        classes_by_id = {
            c.id: c for c in db.query(CharacterClass).filter(CharacterClass.id.in_(
                c.character_class_id for c in self.record.class_map
            )).all()
        }

        assigned = [int(m.class_attribute_id) for m in self.record.character_class_attribute_map]
        logging.debug(f"{assigned = }")

        # step through the list of class mappings for this character
        for class_map in self.record.class_map:
            thisclass = classes_by_id[class_map.character_class_id]

            # assign each class attribute available at the character's current
            # level to the list of the character's class attributes
            for attr_map in [a for a in thisclass.attributes if a.level <= class_map.level]:

                # when creating a record, assign the first of the available
                # options to the character's class attribute.
                default_option = db.query(ClassAttributeOption).filter_by(
                    attribute_id=attr_map.class_attribute_id
                ).first()

                if attr_map.class_attribute_id not in assigned:
                    self.record.class_attributes.append({
                        'class_attribute_id': attr_map.class_attribute_id,
                        'option_id': default_option.id,
                    })

    def save_callback(self):
        self.add_class_attributes()

    def populate(self):
        """
        Delete the association proxies' form data before calling form.populate_obj(),
        and instead use our own methods for populating the fieldlist.
        """

        # multiclass form
        classes_formdata = self.form.data['classes']
        classes_formdata.append(self.form.data['newclass'])
        del self.form.classes
        del self.form.newclass

        # class attributes
        attrs_formdata = self.form.data['class_attributes']
        del self.form.class_attributes

        super().populate()

        self.record.classes = self.populate_association('character_class_id', classes_formdata)
        self.record.class_attributes = self.populate_association('class_attribute_id', attrs_formdata)
