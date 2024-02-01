import logging
from collections import defaultdict

from wtforms_sqlalchemy.orm import model_form

from ttfrog.db.manager import db


class BaseController:
    model = None

    def __init__(self, request):
        self.request = request
        self.attrs = defaultdict(str)
        self.record = None
        self.model_form = None

        self.config = {
            'static_url': '/static',
            'project_name': 'TTFROG'
        }

        self.configure()
        self.configure_for_model()

    def configure_for_model(self):
        if not self.model:
            return
        if not self.model_form:
            self.model_form = model_form(self.model, db_session=db.session)
        if not self.record:
            self.record = self.load_from_slug() or self.load_from_id()

        if 'all_records' not in self.attrs:
            self.attrs['all_records'] = db.query(self.model).all()

    def configure(self):
        pass

    def load_from_slug(self):
        if not self.model:
            return

        parts = self.request.matchdict.get('uri', '').split('/')
        if not parts:
            return
        try:
            return db.query(self.model).filter(self.model.slug == parts[0])[0]
        except IndexError:
            logging.warning(f"Could not load record with slug {parts[0]}")

    def load_from_id(self):
        post_id = self.request.POST.get('id', None)
        if not post_id:
            return
        return db.query(self.model).get(post_id)

    def form(self) -> str:
        if not self.model:
            return

        if self.request.method == 'POST':
            if not self.record:
                self.record = self.model()
            form = self.model_form(self.request.POST, obj=self.record)
            if self.model.validate(form):
                form.populate_obj(self.record)
                if not self.record.id:
                    with db.transaction():
                        db.session.add(self.record)
                        logging.debug(f"Added {self.record = }")
                return form
        return self.model_form(obj=self.record)

    def output(self, **kwargs) -> dict:
        return dict(
            config=self.config,
            request=self.request,
            record=self.record or '',
            form=self.form() or '',
            **self.attrs,
            **kwargs,
        )

    def response(self):
        return self.output()
