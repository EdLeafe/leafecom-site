import logging
from subprocess import Popen, PIPE

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class UptimeController(BaseController):

    def index(self):
		proc = Popen(["uptime"], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
		uptext = proc.stdout.read()
		proc = Popen(["df"], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
		df = proc.stdout.read()
		dftext = "".join([ln for ln in df.splitlines()
				if "sda" in ln])
		ret = """<h1>Uptime</h1>
<h3>%s</h3>
<h1>Disk</h1>
<h3>%s</h3>"""
		return ret % (uptext, dftext)

