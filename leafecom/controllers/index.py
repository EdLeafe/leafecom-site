import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect
from pylons import tmpl_context as c
from pylons.templating import render_mako as render

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class IndexController(BaseController):

    def index(self):
        # Return a rendered template
        #return render('/index.mako')
        # or, return a response
        return render("index.html")
