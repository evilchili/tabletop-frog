from ttfrog.webserver.controllers import BaseController
from ttfrog.db.schema import Character


class CharacterSheet(BaseController):
    model = Character
