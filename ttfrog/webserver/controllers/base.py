from collections import defaultdict

from wtforms_sqlalchemy.orm import model_form

from ttfrog.db.manager import db


class BaseController:
    model = None

    def __init__(self, request):
        self.request = request
        self.record = None
        self.attrs = defaultdict(str)
        self.configure()
        if self.model:
            self.model_form = model_form(self.model, db_session=db.session)

        # load this from dotenv or something
        self.config = {
            'static_url': '/static',
            'project_name': 'TTFROG'
        }

    def configure(self):
        self.load_from_id()

    def load_from_id(self):
        if not self.request.POST['id']:
            return
        self.record = db.query(self.model).get(self.request.POST['id'])

    def form(self) -> str:
        # no model? no form.
        if not self.model:
            return ''

        if self.request.method == 'POST':
            form = self.model_form(self.request.POST, obj=self.record)
            if self.model.validate(form):
                form.populate_obj(self.record)
                return form
        return self.model_form(obj=self.record)

    def output(self, **kwargs) -> dict:
        return dict(
            config=self.config,
            request=self.request,
            record=self.record,
            form=self.form(),
            **self.attrs,
            **kwargs,
        )

    def response(self):
        return self.output()
