from ttfrog.db.manager import db
from wtforms.fields import SelectField, SelectMultipleField

class DeferredSelectMultipleField(SelectMultipleField):
    def __init__(self, *args, model=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = [(rec.id, rec.name) for rec in db.query(model).all()]


class DeferredSelectField(SelectField):
    def __init__(self, *args, model=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = [(rec.id, rec.name) for rec in db.query(model).all()]
