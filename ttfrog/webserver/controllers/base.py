import logging
import re

from collections import defaultdict

from pyramid.httpexceptions import HTTPFound
from pyramid.interfaces import IRoutesMapper

from sqlalchemy.inspection import inspect

from ttfrog.attribute_map import AttributeMap
from ttfrog.db.manager import db


def get_all_routes(request):
    routes = {
        'static': '/static',
    }
    uri_pattern = re.compile(r"^([^\{\*]+)")
    mapper = request.registry.queryUtility(IRoutesMapper)
    for route in mapper.get_routes():
        if route.name.startswith('__'):
            continue
        m = uri_pattern.search(route.pattern)
        if m:
            routes[route.name] = m .group(0)
    return routes


def query_factory(model):
    return lambda: db.query(model).all()


class BaseController:
    model = None
    model_form = None

    def __init__(self, request):
        self.request = request
        self.attrs = defaultdict(str)
        self._slug = None
        self._record = None
        self._form = None

        self.config = {
            'static_url': '/static',
            'project_name': 'TTFROG'
        }
        self.configure_for_model()

    @property
    def slug(self):
        if not self._slug:
            parts = self.request.matchdict.get('uri', '').split('-')
            self._slug = parts[0].replace('/', '')
        return self._slug

    @property
    def record(self):
        if not self._record and self.model:
            try:
                self._record = db.query(self.model).filter(self.model.slug == self.slug)[0]
            except IndexError:
                logging.warning(f"Could not load record with slug {self.slug}")
                self._record = self.model()
        return self._record

    @property
    def form(self):
        if not self.model:
            return
        if not self._form:
            if self.request.POST:
                self._form = self.model_form(self.request.POST, obj=self.record)
            else:
                self._form = self.model_form(obj=self.record)
        return self._form

    def configure_for_model(self):
        if 'all_records' not in self.attrs:
            self.attrs['all_records'] = db.query(self.model).all()

    def coerce_foreign_keys(self):
        inspector = inspect(db.engine)
        foreign_keys = inspector.get_foreign_keys(table_name=self.record.__class__.__tablename__)
        for foreign_key in foreign_keys:
            for col in inspector.get_columns(foreign_key['referred_table']):
                if col['name'] == foreign_key['referred_columns'][0]:
                    col_name = foreign_key['constrained_columns'][0]
                    col_type = col['type'].python_type
                    col_value = col_type(getattr(self.record, col_name))
                    setattr(self.record, col_name, col_value)

    def template_context(self, **kwargs) -> dict:
        return AttributeMap.from_dict({
            'c': dict(
                config=self.config,
                request=self.request,
                form=self.form,
                record=self.record,
                routes=get_all_routes(self.request),
                **self.attrs,
                **kwargs,
            )
        })

    def save(self):
        if not self.form.save.data:
            return
        if not self.form.validate():
            return
        self.form.populate_obj(self.record)
        self.coerce_foreign_keys()
        if self.record.id:
            return
        with db.transaction():
            db.add(self.record)
            logging.debug(f"Added {self.record = }")
            location = f"{self.request.current_route_path()}/{self.record.uri}"
            return HTTPFound(location=location)

    def delete(self):
        if not self.record.id:
            return
        with db.transaction():
            db.query(self.model).filter_by(id=self.record.id).delete()
            logging.debug(f"Deleted {self.record = }")
            location = self.request.current_route_path()
            return HTTPFound(location=location)

    def response(self):
        if not self.form:
            return
        elif self.form.save.data:
            return self.save()
        elif self.form.delete.data:
            return self.delete()
