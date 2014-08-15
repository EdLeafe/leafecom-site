import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class RentalsController(BaseController):

    def index(self):
        # Return a rendered template
        #return render('/rentals.mako')
        # or, return a string
        return "This is the rentals page"

