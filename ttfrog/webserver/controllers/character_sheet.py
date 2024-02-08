from ttfrog.webserver.controllers.base import BaseController
from ttfrog.webserver.forms import DeferredSelectField, DeferredSelectMultipleField
from ttfrog.db.schema import Character, Ancestry, CharacterClass, STATS
from wtforms_alchemy import ModelForm
from wtforms.fields import SubmitField, SelectMultipleField
from wtforms.widgets import Select


class CharacterForm(ModelForm):
    class Meta:
        model = Character
        exclude = ['slug']

    save = SubmitField()
    delete = SubmitField()

    ancestry = DeferredSelectField('Ancestry', model=Ancestry, validate_choice=True, widget=Select())

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
