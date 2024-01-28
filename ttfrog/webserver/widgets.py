import tw2.core
import tw2.forms
from tg import lurl


class CharacterSheet(tw2.forms.Form):
    class child(tw2.forms.TableLayout):
        name = tw2.forms.TextField()
        level = tw2.forms.TextField()
        ancestry_name = tw2.forms.TextField(label='Ancestry')
        id = tw2.forms.HiddenField()

    action = ''
