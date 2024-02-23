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


class NullableDeferredSelectField(DeferredSelectField):
    def __init__(self, *args, model=None, label='---',  **kwargs):
        super().__init__(*args, model=model,  **kwargs)
        self.choices = [(0, label)] + self.choices
