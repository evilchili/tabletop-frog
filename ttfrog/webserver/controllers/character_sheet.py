import base64
import hashlib
import logging

from tg import expose
from tg import flash
from tg import validate
from tg.controllers.util import redirect
from ttfrog.db import db
from ttfrog.db.schema import Character
from ttfrog.webserver.controllers.base import BaseController
from ttfrog.webserver.widgets import CharacterSheet


class CharacterSheetController(BaseController):
    @expose()
    def _lookup(self, *parts):
        slug = parts[0] if parts else ''
        return FormController(slug), parts[1:] if len(parts) > 1 else []


class FormController(BaseController):

    def __init__(self, slug: str):
        super().__init__()
        self.character = dict()
        if slug:
            self.load_from_slug(slug)

    @property
    def uri(self):
        if self.character:
            return f"/sheet/{self.character['slug']}/{self.character['name']}"
        else:
            return None

    @property
    def all_characters(self):
        return [row._mapping for row in db.query(Character).all()]

    def load_from_slug(self, slug) -> None:
        self.character = db.query(Character).filter(Character.columns.slug == slug)[0]._mapping

    def save(self, fields) -> str:
        rec = dict()
        if not self.character:
            result, error = db.insert(Character, **fields)
            if error:
                return error
            fields['id'] = result.inserted_primary_key[0]
            fields['slug'] = db.slugify(fields)
        else:
            rec = dict(**self.character)

        rec.update(**fields)
        result, error = db.update(Character, **rec)
        self.load_from_slug(rec['slug'])
        if not error:
            flash(f"{self.character['name']} updated!")
            return redirect(self.uri)
        flash(error)

    @expose('character_sheet.html')
    @validate(form=CharacterSheet)
    def _default(self, *args, **fields):
        if fields:
            return self.save(fields)
        return self.output(
            form=CharacterSheet,
            character=self.character,
            all_characters=self.all_characters,
        )
