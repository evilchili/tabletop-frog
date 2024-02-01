import logging

from ttfrog.webserver.controllers import BaseController
from ttfrog.db.manager import db
from ttfrog.db.schema import Character


class CharacterSheet(BaseController):
    model = Character

    def configure(self):
        self.attrs['all_characters'] = db.query(Character).all()
        slug = self.request.matchdict.get('slug', None)
        if slug:
            try:
                self.record = db.query(Character).filter(Character.slug == slug)[0]
            except IndexError:
                logging.warning(f"Could not load record with slug {slug}")
        else:
            self.load_from_id()
