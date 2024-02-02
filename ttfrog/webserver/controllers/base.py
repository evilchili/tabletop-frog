import logging
import re
from collections import defaultdict

from wtforms_sqlalchemy.orm import model_form

from pyramid.httpexceptions import HTTPFound
from pyramid.interfaces import IRoutesMapper

from ttfrog.db.manager import db


def get_all_routes(request):
    uri_pattern = re.compile(r"^([^\{\*]+)")
    mapper = request.registry.queryUtility(IRoutesMapper)
    routes = {}
    for route in mapper.get_routes():
        if route.name.startswith('__'):
            continue
        m = uri_pattern.search(route.pattern)
        if m:
            routes[route.name] = m .group(0)
    return routes


class BaseController:
    model = None

    def __init__(self, request):
        self.request = request
        self.attrs = defaultdict(str)
        self.record = None
        self.form = None
        self.model_form = None

        self.config = {
            'static_url': '/static',
            'project_name': 'TTFROG'
        }
        self.configure_for_model()
        self.configure()

    def configure_for_model(self):
        if not self.model:
            return
        if not self.model_form:
            self.model_form = model_form(self.model, db_session=db.session)
        if not self.record:
            self.record = self.get_record_from_slug()

        if 'all_records' not in self.attrs:
            self.attrs['all_records'] = db.query(self.model).all()

    def configure(self):
        pass

    def get_record_from_slug(self):
        if not self.model:
            return
        parts = self.request.matchdict.get('uri', '').split('-')
        if not parts:
            return
        slug = parts[0].replace('/', '')
        if not slug:
            return
        try:
            return db.query(self.model).filter(self.model.slug == slug)[0]
        except IndexError:
            logging.warning(f"Could not load record with slug {slug}")

    def process_form(self):
        if not self.model:
            return False

        if self.request.method == 'POST':

            # if we haven't loaded a record, we're creating a new one
            if not self.record:
                self.record = self.model()

            # generate a form object using the POST form data and the db record
            self.form = self.model_form(self.request.POST, obj=self.record)
            if self.model.validate(self.form):
                # update the record. If it's a record bound to the session
                # updates will be commited automatically. Otherwise we must
                # add and commit the record.
                self.form.populate_obj(self.record)
                if not self.record.id:
                    with db.transaction():
                        db.session.add(self.record)
                        logging.debug(f"Added {self.record = }")
                        return True
                return False
        self.form = self.model_form(obj=self.record)
        return False

    def output(self, **kwargs) -> dict:
        return dict(c=dict(
            config=self.config,
            request=self.request,
            form=self.form,
            record=self.record,
            routes=get_all_routes(self.request),
            **self.attrs,
            **kwargs,
        ))

    def response(self):
        if self.process_form():
            return HTTPFound(location=f"{self.request.current_route_path}/{self.record.uri}")
        return self.output()
