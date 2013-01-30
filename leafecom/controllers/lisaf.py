import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class LisafController(BaseController):

	def index(self):
		# Return a rendered template
		#return render('/lisaf.mako')
		# or, return a response
		return 'Hello World'


	def testing(self):
		return "COOL"
