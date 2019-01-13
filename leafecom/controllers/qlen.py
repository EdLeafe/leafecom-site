import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class QlenController(BaseController):
    def index(self):
        return "%s" % len(request.query_string)

