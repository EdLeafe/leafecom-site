import logging
import os

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect, redirect
from pylons import app_globals
from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class DownloadController(BaseController):

	def GET(self, url):
		log.info("[IP: %s] File request: %s" % (request.remote_addr, url))
		try:
			 url.encode("latin-1")
		except UnicodeEncodeError:
			# Pylons seems to require latin-1
			url = url.encode("utf8").decode("latin-1")
			log.info("  Request re-encoded to: %s" % url)
		pth = os.path.join(app_globals.CDNBASE, url)
		redirect(pth)
