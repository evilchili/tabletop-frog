from pyramid.response import Response
from pyramid.view import view_config

from ttfrog.attribute_map import AttributeMap
from ttfrog.db.manager import db
from ttfrog.db.schema import Ancestry


def response_from(controller):
    return controller.response() or AttributeMap.from_dict({"c": controller.template_context()})


@view_config(route_name="index")
def index(request):
    ancestries = [a.name for a in db.session.query(Ancestry).all()]
    return Response(",".join(ancestries))


@view_config(route_name="sheet", renderer="character_sheet.html")
def sheet(request):
    return response_from(request.context)


@view_config(route_name="data", renderer="json")
def data(request):
    return response_from(request.context)
