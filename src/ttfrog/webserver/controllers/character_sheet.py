import logging

from markupsafe import Markup
from wtforms import ValidationError
from wtforms.fields import FieldList, FormField, HiddenField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import Optional
from wtforms.widgets import ListWidget, Select
from wtforms.widgets.core import html_params
from wtforms_alchemy import ModelForm

from ttfrog.db.base import STATS
from ttfrog.db.manager import db
from ttfrog.db.schema import (
    Ancestry,
    Character,
    CharacterClass,
    CharacterClassAttributeMap,
    CharacterClassMap,
    ClassAttributeOption,
)
from ttfrog.webserver.controllers.base import BaseController
from ttfrog.webserver.forms import DeferredSelectField, NullableDeferredSelectField

VALID_LEVELS = range(1, 21)


class ClassAttributeWidget:
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = [
            f"<span {html_params(**kwargs)}>{field.character_class_map.class_attribute.name}</span>",
            "<span>",
        ]
        for subfield in field:
            html.append(subfield())
        html.append("</span>")
        return Markup("".join(html))


class ClassAttributesFormField(FormField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.character_class_map = None

    def process(self, *args, **kwargs):
        super().process(*args, **kwargs)
        self.character_class_map = db.query(CharacterClassAttributeMap).get(self.data["id"])
        if self.character_class_map:
            self.label.text = self.character_class_map.character_class.name


class ClassAttributesForm(ModelForm):
    id = HiddenField()
    class_attribute_id = HiddenField()

    option_id = SelectField(widget=Select(), choices=[], validators=[Optional()], coerce=int)

    def __init__(self, formdata=None, obj=None, prefix=None):
        if obj:
            logging.debug(f"Loading existing attribute {self = } {formdata = } {obj = }")
            obj = db.query(CharacterClassAttributeMap).get(obj)
        super().__init__(formdata=formdata, obj=obj, prefix=prefix)

        if obj:
            options = db.query(ClassAttributeOption).filter_by(attribute_id=obj.class_attribute.id)
            self.option_id.choices = [(rec.id, rec.name) for rec in options.all()]


class MulticlassForm(ModelForm):
    id = HiddenField()
    character_class_id = NullableDeferredSelectField(
        model=CharacterClass, validate_choice=True, widget=Select(), coerce=int
    )
    level = SelectField(choices=VALID_LEVELS, default=1, coerce=int, validate_choice=True, widget=Select())

    def __init__(self, formdata=None, obj=None, prefix=None):
        """
        Populate the form field with a CharacterClassMap object by converting the object ID
        to an instance. This will ensure that the rendered field is populated with the current
        value of the class_map.
        """
        logging.debug(f"Loading existing class {self = } {formdata = } {obj = }")
        if obj:
            obj = db.query(CharacterClassMap).get(obj)
        super().__init__(formdata=formdata, obj=obj, prefix=prefix)


class CharacterForm(ModelForm):
    class Meta:
        model = Character
        exclude = ["slug"]

    save = SubmitField()
    delete = SubmitField()
    ancestry_id = DeferredSelectField("Ancestry", model=Ancestry, default=1, validate_choice=True, widget=Select())
    class_list = FieldList(FormField(MulticlassForm, label=None, widget=ListWidget()), min_entries=0)
    newclass = FormField(MulticlassForm, widget=ListWidget())

    attribute_list = FieldList(
        ClassAttributesFormField(ClassAttributesForm, widget=ClassAttributeWidget()), min_entries=1
    )

    saving_throws = SelectMultipleField("Saving Throws", validate_choice=True, choices=STATS)


class CharacterSheet(BaseController):
    model = CharacterForm.Meta.model
    model_form = CharacterForm

    @property
    def resources(self):
        return super().resources + [
            {"type": "script", "uri": "js/character_sheet.js"},
        ]

    def validate_callback(self):
        """
        Validate multiclass fields in form data.
        """
        ret = super().validate()
        if not self.form.data["class_list"]:
            return ret

        err = ""
        total_level = 0
        for field in self.form.data["class_list"]:
            level = field.get("level")
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
        # step through the list of class mappings for this character
        for class_name, class_def in self.record.classes.items():
            logging.error(f"{class_name = }, {class_def = }")
            for level in range(1, self.record.levels[class_name] + 1):
                for attr in class_def.attributes_by_level.get(level, None):
                    self.record.add_class_attribute(attr, attr.options[0])

    def save_callback(self):
        #  self.add_class_attributes()
        pass

    def populate(self):
        """
        Delete the association proxies' form data before calling form.populate_obj(),
        and instead use our own methods for populating the fieldlist.
        """

        # multiclass form
        classes_formdata = self.form.data["class_list"]
        classes_formdata.append(self.form.data["newclass"])
        del self.form.class_list
        del self.form.newclass

        # class attributes
        attrs_formdata = self.form.data["attribute_list"]
        del self.form.attribute_list

        super().populate()

        self.record.class_list = self.populate_association("character_class_id", classes_formdata)
        self.record.attribute_list = self.populate_association("class_attribute_id", attrs_formdata)
