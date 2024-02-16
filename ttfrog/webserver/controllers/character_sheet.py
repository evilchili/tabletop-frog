from ttfrog.webserver.controllers.base import BaseController
from ttfrog.webserver.forms import DeferredSelectField, DeferredSelectMultipleField
from ttfrog.db.schema import Character, Ancestry, CharacterClass, AncestryTrait, Modifier, STATS
from ttfrog.db.manager import db
from ttfrog.attribute_map import AttributeMap

from wtforms_alchemy import ModelForm
from wtforms.fields import SubmitField, SelectMultipleField
from wtforms.widgets import Select


class CharacterForm(ModelForm):
    class Meta:
        model = Character
        exclude = ['slug']

    save = SubmitField()
    delete = SubmitField()

    ancestry = DeferredSelectField('Ancestry', model=Ancestry, default='human', validate_choice=True, widget=Select())

    character_class = DeferredSelectMultipleField(
        'CharacterClass',
        model=CharacterClass,
        validate_choice=True,
        #  option_widget=Select(multiple=True)
    )

    saving_throws = SelectMultipleField('Saving Throws', validate_choice=True, choices=STATS)


class CharacterSheet(BaseController):
    model = CharacterForm.Meta.model
    model_form = CharacterForm

    @property
    def resources(self):
        return super().resources + [
            {'type': 'script', 'uri': 'js/character_sheet.js'},
        ]

    def template_context(self, **kwargs) -> dict:
        ctx = super().template_context(**kwargs)
        if self.record.ancestry:
            ancestry = db.query(Ancestry).filter_by(name=self.record.ancestry).one()
            ctx['traits'] = {}
            for trait in db.query(AncestryTrait).filter_by(ancestry_id=ancestry.id).all():
                ctx['traits'][trait.description] = db.query(Modifier).filter_by(source_table_name=trait.__tablename__, source_table_id=trait.id).all()
        else:
            ctx['traits'] = {};
        return ctx
