import logging
import re

from collections import defaultdict

from pyramid.httpexceptions import HTTPFound
from pyramid.interfaces import IRoutesMapper

from ttfrog.db.manager import db
from ttfrog.db import transaction_log


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
        if not self.model_form:
            return
        if not self._form:
            if self.request.POST:
                self._form = self.model_form(self.request.POST, obj=self.record)
            else:
                self._form = self.model_form(obj=self.record)
                if not self.record.id:
                    # apply the db schema defaults
                    self._form.process()
        return self._form

    @property
    def resources(self):
        return [
            {'type': 'style', 'uri': 'css/styles.css'},
        ]

    def configure_for_model(self):
        if 'all_records' not in self.attrs:
            self.attrs['all_records'] = db.query(self.model).all()

    def template_context(self, **kwargs) -> dict:
        return dict(
            config=self.config,
            request=self.request,
            form=self.form,
            record=self.record,
            routes=get_all_routes(self.request),
            resources=self.resources,
            **self.attrs,
            **kwargs,
        )

    def populate(self):
        self.form.populate_obj(self.record)

    def populate_association(self, key, formdata):
        populated = []
        for field in formdata:
            map_id = field.pop('id')
            map_id = int(map_id) if map_id else 0
            if not field[key]:
                continue
            elif not map_id:
                populated.append(field)
            else:
                field['id'] = map_id
                populated.append(field)
        return populated

    def validate(self):
        return self.form.validate()

    def save(self):
        if not self.form.save.data:
            return
        if not self.validate():
            return
        logging.debug(f"{self.form.data = }")
        # previous = dict(self.record)
        logging.debug(f"{self.record = }")
        self.populate()
        # transaction_log.record(previous, self.record)
        with db.transaction():
            db.add(self.record)
            self.save_callback()
            logging.debug(f"Saved {self.record = }")
            location = self.request.current_route_path()
            if self.record.slug not in location:
                location = f"{location}/{self.record.uri}"
            logging.debug(f"Redirecting to {location}")
            return HTTPFound(location=location)

    def delete(self):
        if not self.record.id:
            return
        with db.transaction():
            db.query(self.model).filter_by(id=self.record.id).delete()
            location = self.request.current_route_path()
            return HTTPFound(location=location)

    def response(self):
        if not self.form:
            return
        elif self.form.save.data:
            return self.save()
        elif self.form.delete.data:
            return self.delete()
