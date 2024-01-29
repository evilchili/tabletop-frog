import inspect

from tg import flash
from tg import TGController
from tg import tmpl_context
from markupsafe import Markup


class BaseController(TGController):

    def _before(self, *args, **kwargs):
        tmpl_context.project_name = 'TableTop Frog'

    def output(self, **kwargs) -> dict:
        return dict(
            page=inspect.stack()[1].function,
            flash=Markup(flash.render('flash', use_js=False)),
            **kwargs,
        )
