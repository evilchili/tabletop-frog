from pyramid.httpexceptions import exception_response

from ttfrog.db import schema
from ttfrog.db.manager import db

from .base import BaseController


class JsonData(BaseController):
    model = None
    model_form = None

    def configure_for_model(self):
        try:
            self.model = getattr(schema, self.request.matchdict.get("table_name"))
        except AttributeError:
            raise exception_response(404)

    def response(self):
        query = db.query(self.model).filter_by(**self.request.params)
        return {"table_name": self.model.__tablename__, "records": query.all()}
