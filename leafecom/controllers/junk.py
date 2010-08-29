import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify
from decorator import decorator

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)



def poop(func, *args, **kwargs):
	 data = func(*args, **kwargs)
	 return "POOP"
poop = decorator(poop)



class JunkController(BaseController):

	def index(self):
		# Return a rendered template
		#return render('/junk.mako')
		# or, return a response
		return 'Hello World'


	def regurgitate(self, id):
		return str(id)


	@poop
	def crap(self):
		return [{"ticket_number": "091113-02832", "team": "Team I-3", "source": "Customer", "created": "2009-11-13 10:00:16"}, 
				{"ticket_number": "091113-02833", "team": "Team M9", "source": "Customer", "created": "2009-11-13 10:00:23"}, 
				{"ticket_number": "091113-02834", "team": "Team M8", "source": "Customer", "created": "2009-11-13 10:00:25"}, 
				{"ticket_number": "091113-02835", "team": "Team I-3", "source": "Customer", "created": "2009-11-13 10:00:32"}, 
				{"ticket_number": "091113-02836", "team": "Team UK M2", "source": "Customer", "created": "2009-11-13 10:00:34"}, 
				{"ticket_number": "091113-02837", "team": "Team C1", "source": "Auto", "created": "2009-11-13 10:00:44"}, 
				{"ticket_number": "091113-02838", "team": "Team I-3", "source": "Customer", "created": "2009-11-13 10:00:53"},
				{"ticket_number": "091113-02875", "team": "Team C1", "source": "Customer", "created": "2009-11-13 10:03:38"}]



