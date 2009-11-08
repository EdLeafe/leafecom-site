import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class ConsultingController(BaseController):

	def index(self, id=None):
		if id == "resume":
			return render("/resume.html")
		else:
			return render("/consulting.html")
