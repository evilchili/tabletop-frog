from ttfrog.db.schema import Ancestry
from ttfrog.db.manager import db
from wtforms_alchemy import ModelForm


class AncestryForm(ModelForm):
    class Meta:
        model = Ancestry
        exclude = ['slug']

    def get_session():
        return db.session
