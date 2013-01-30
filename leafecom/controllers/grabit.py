import logging
import os

from pylons import request, response, session, tmpl_context as c
from pylons import app_globals
from pylons.controllers.util import abort, redirect

from dabo.lib.base import BaseController, render

log = logging.getLogger(__name__)

class GrabitController(BaseController):

    def index(self, url):
		log.info("File request: %s" % url)
		pth = str(os.path.join(app_globals.CDNBASE, url))
		redirect(pth)
