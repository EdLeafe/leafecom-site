import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class PyexifController(BaseController):

    def index(self):
		return render("pyexif.html")
