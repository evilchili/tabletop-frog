from pyramid.response import Response
from pyramid.view import view_config
from ttfrog.db.manager import db
from ttfrog.db.schema import Ancestry


@view_config(route_name='index')
def index(request):
    ancestries = [a.name for a in db.session.query(Ancestry).all()]
    return Response(','.join(ancestries))


@view_config(route_name='sheet', renderer='character_sheet.html')
def sheet(request):
    controller = request.context
    return controller.response() or controller.template_context()
