from pyramid.response import Response
from pyramid.view import view_config
from ttfrog.db.manager import db
from ttfrog.db.schema import Ancestry


@view_config(route_name='index')
def index(request):
    ancestries = [a.name for a in db.session.query(Ancestry).all()]
    return Response(','.join(ancestries))
