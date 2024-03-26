from wtforms_alchemy import ModelForm

from ttfrog.db.manager import db
from ttfrog.db.schema import Ancestry


class AncestryForm(ModelForm):
    class Meta:
        model = Ancestry
        exclude = ["slug"]

    def get_session():
        return db.session
