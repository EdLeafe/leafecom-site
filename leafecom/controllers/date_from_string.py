import logging

from mx import DateTime
from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class DateFromStringController(BaseController):

    def index(self, id=None):
        # Return a rendered template
        #return render('/date_from_string.mako')
        # or, return a response
		if id:
			try:
				dt = DateTime.Parser.DateTimeFromString(id)
				return dt.strftime("%Y-%m-%d %H:%M:%S")
			except StandardError as e:
				return "Error: %s" %e
			return "You passed: %s" % id
		else:
			return 'Hello World'
