import tw2.core as twc
import tw2.forms
from ttfrog.db import db


class CharacterSheet(tw2.forms.Form):
    action = ''

    class child(tw2.forms.TableLayout):
        name = tw2.forms.TextField(validator=twc.Required)
        level = tw2.forms.SingleSelectField(
            prompt_text=None,
            options=range(1, 21),
            validator=twc.validation.IntValidator(min=1, max=20)
        )
        ancestry_name = tw2.forms.SingleSelectField(
            label='Ancestry',
            prompt_text=None,
            options=twc.Deferred(lambda: [a.name for a in db.query(db.ancestry)]),
            validator=twc.Required,
        )
