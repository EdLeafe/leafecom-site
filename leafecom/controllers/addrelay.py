import logging
import os

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render
import leafecom.lib.helpers as h

log = logging.getLogger(__name__)



class AddrelayController(BaseController):

	def index(self):
		# Return a rendered template
		#return render('/addrelay.mako')
		# or, return a response
		mthd = request.method
		log.info("METHOD: %s", mthd)
		if mthd == "POST":
			return self._set_relay()
		elif mthd == "GET":
			log.error("PATH: %s" % request.path)
			pth = request.path.split("/")[-1]
			log.error("PTH: %s" % pth)
			if pth == "roam":
				return self._set_roam_address()
			return h.get_location_addr(pth)


	def _set_roam_address(self):
		log.error("IN _set_roam_address")
		return self._write_relay("roaming", request.remote_addr)


	def _set_relay(self):
		params = request.params
		loc = params.keys()[0]
		addr = params.get(loc)
		return self._write_relay(loc, addr)


	def _write_relay(self, loc, addr):
		log.error("IN _write_relay, loc=%s, addr=%s" % (loc, addr))
		main_text_lines = file(h.MAIN_CONF).readlines()
		log.error("TEXT LINES: %s" % len(main_text_lines))
		mtch = "%s =" % loc
		match_lines = [(pos, ln.strip()) for pos, ln in enumerate(main_text_lines)
				if ln.startswith(mtch)]
		log.error("MATCH LINES: %s" % len(match_lines))
		if not match_lines:
			return "No such location: '%s'" % loc
		mpos = match_lines[0][0]
		mln = match_lines[0][1]
		newln = "%s = %s\n" % (loc, addr)
		main_text_lines[mpos] = newln
		newtext = "".join(main_text_lines)
		log.error("before write_conf")
		err, out = h.write_conf(newtext, log)
		log.error("after write_conf")
		if not err:
			os.system("sudo /zinitd/postfix reload")
			return "Address %s has been included." % addr
