from tg import expose

from ttfrog.db import db
from ttfrog.webserver.controllers.base import BaseController
from ttfrog.webserver.controllers.character_sheet import CharacterSheetController


class RootController(BaseController):

    # serve character sheet interface on /sheet
    sheet = CharacterSheetController()

    @expose('index.html')
    def index(self):
        ancestries = [row._mapping for row in db.query(db.ancestry).all()]
        return self.output(content=str(ancestries))
