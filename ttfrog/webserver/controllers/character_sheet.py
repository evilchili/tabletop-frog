from ttfrog.webserver.controllers.base import BaseController, DeferredSelectField
from ttfrog.db.schema import Character, Ancestry
from wtforms_alchemy import ModelForm
from wtforms.fields import SubmitField


class CharacterForm(ModelForm):
    class Meta:
        model = Character
        exclude = ['slug']

    save = SubmitField()
    delete = SubmitField()
    ancestry = DeferredSelectField('Ancestry', model=Ancestry, coerce=str, validate_choice=True)


class CharacterSheet(BaseController):
    model = CharacterForm.Meta.model
    model_form = CharacterForm
