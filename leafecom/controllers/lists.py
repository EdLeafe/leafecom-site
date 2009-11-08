import leafecom.lib.helpers as h
import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class ListsController(BaseController):

	def index(self):
		return render("lists.html")
