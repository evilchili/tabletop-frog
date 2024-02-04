from wtforms_alchemy import ModelForm
from db.schema import Character


class CharacterForm(ModelForm):
    class Meta:
        model = Character
