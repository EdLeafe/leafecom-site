import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class AddaliasController(BaseController):

    def index(self):
        # Return a rendered template
        #return render('/addalias.mako')
        # or, return a response
        return 'Hello World'
