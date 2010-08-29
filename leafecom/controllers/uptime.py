import logging
from subprocess import Popen, PIPE

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class UptimeController(BaseController):

    def index(self):
		proc = Popen(["uptime"], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
		return proc.stdout.read()

