from tg import expose
from tg import TGController
from ttfrog.db import db
from ttfrog.db.schema import Character
from ttfrog.webserver.widgets import CharacterSheet


class CharacterSheetController(TGController):
    @expose()
    def _lookup(self, *parts):
        return FormController(parts[0]), parts[1:]


class FormController:

    def __init__(self, slug: str):
        self.character = dict()
        if slug:
            self.load(slug)

    def load(self, slug: str) -> None:
        self.character = db.query(Character).filter(Character.columns.slug == slug)[0]._mapping

    @expose('character_sheet.html')
    def _default(self, *args, **kwargs):
        if kwargs:
            db.update(Character, **kwargs)
            self.load(self.character['slug'])
        return dict(page='sheet', form=CharacterSheet, character=self.character)
