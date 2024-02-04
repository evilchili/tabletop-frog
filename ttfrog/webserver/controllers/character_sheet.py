from ttfrog.webserver.controllers.base import BaseController, query_factory
from ttfrog.db.schema import Character, Ancestry
from ttfrog.db.manager import db
from wtforms_alchemy import ModelForm, QuerySelectField
from wtforms.validators import InputRequired
from wtforms.fields import SubmitField


class CharacterForm(ModelForm):
    class Meta:
        model = Character
        exclude = ['slug']

    def get_session():
        return db.session

    save = SubmitField()
    delete = SubmitField()

    ancestry = QuerySelectField('Ancestry', validators=[InputRequired()],
                                query_factory=query_factory(Ancestry), get_label='name')


class CharacterSheet(BaseController):
    model = CharacterForm.Meta.model
    model_form = CharacterForm
