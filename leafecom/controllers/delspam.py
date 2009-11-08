import os
import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class DelspamController(BaseController):

	def index(self, id):
		fname = os.path.join("/home/ed/spam/checked", id)
		try:
			os.unlink(fname)
			return "<h2>File %s has been deleted.</h2>" % id
		except OSError, e:
			return "Couldn't delete it: %s" %  e
