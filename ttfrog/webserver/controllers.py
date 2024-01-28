from tg import expose
from tg import TGController
from tg import tmpl_context
from ttfrog.db import db
from ttfrog.db.schema import Character


class RootController(TGController):

    def _before(self, *args, **kwargs):
        tmpl_context.project_name = 'TableTop Frog'

    @expose('index.html')
    def index(self):
        ancestries = [row._mapping for row in db.query(db.ancestry).all()]
        return dict(page='index', content=str(ancestries))
