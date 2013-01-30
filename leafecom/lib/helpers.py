#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password

import datetime
import inspect
import logging
import random
import re
from subprocess import Popen, PIPE
from textwrap import TextWrapper
from sqlalchemy.exc import DBAPIError
from pylons import request
from webhelpers.html.tags import file
import leafecom.model.meta as meta


MAIN_CONF = "/etc/postfix/main.cf"
VALID_NAMES = ("leafe_com", "daboserver_com", "argyle_home", "sa_home", "rackspace",
		"iphone", "hotel", "roaming")
copyright = u"Copyright ©%s Ed Leafe" % datetime.datetime.now().year


def runproc(cmd):
	return Popen([cmd], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)


def wrapper(txt):
    tw = TextWrapper(width=100)
    out = []
    for ln in txt.splitlines():
        wrapped = tw.wrap(ln)
        if wrapped:
            out.extend(wrapped)
        else:
            out.extend(" ")
    return "\n".join(out)


def maskEmail(val):
	pat = re.compile("([^@]+)@([^@\.]+)\.([^@]+)")
	ats = ("AT", "at", "At", "(AT)", "(at)", "/at/", "/AT/", ".AT.", ".at.") 
	atString = random.choice(ats)
	dot1 = "DOT" 
	dot = ""
	for ch in dot1:
		if random.randrange(0,2):
			dot += "."
		dot += ch
	return pat.sub("\g<1> " + atString + " \g<2> " + dot + " \g<3>", val)


def _location_line(loc):
	mtch = "%s =" % loc
	cmd = "grep '%s' %s" % (mtch, MAIN_CONF)
	proc = runproc(cmd)
	proc.wait()
	return proc.stdout.read().strip()


def get_location_addr(loc):
	"""Returns the current address for the specified location."""
	# Make sure that the address is valid
	if not loc in VALID_NAMES:
		return "Invalid location: '%s'\n" % loc
	line = _location_line(loc)
	return line.split(" = ")[-1]


def write_conf(txt, log):
	fname = "/tmp/mainconftempfile"
	with open(fname, "w") as tmp:
		tmp.write(txt)
	cmd = "sudo cp %s %s" % (fname, MAIN_CONF)
	proc = runproc(cmd)
	proc.wait()
	return (proc.stderr.read(), proc.stdout.read())


def get_sa_home_ip():
	return get_location_addr("sa_home")


def retry_lost(fnc):
	"""Decorator to help retry connections for the "MySQL has gone away" problem.
	
	The idea is that when this error is encountered, we need to rollback the
	current transaction before SQLAlchemy can re-connect.
	"""
	def _wrapped(*args, **kwargs):
		err = None
		frms = inspect.getouterframes(inspect.currentframe())
		fname = [frm[3] for frm in frms][1]
		log = logging.getLogger(fname)
		for attempt in xrange(5):
			try:
				ret = fnc(*args, **kwargs)
				err = None
				if attempt:
					log.warn("Retry was successful for '%s'." % fname)
				break
			except DBAPIError as err:
				# Try doing this more than once; failing with bots
				log.warn("DBAPIError; attempt #%s; func=%s; ip: %s; url: %s; user_agent: %s" % (attempt, fname,
						request.remote_addr, request.url, request.user_agent))
				meta.Session.rollback()
				continue
		if err:
			log.error("Giving up on function %s" % fname)
			raise err
		else:
			return ret
	return _wrapped
