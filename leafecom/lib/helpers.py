#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password

import datetime
import re
import random
from textwrap import TextWrapper
from webhelpers.html.tags import file

copyright = u"Copyright ©%s Ed Leafe" % datetime.datetime.now().year


def wrapper(txt):
	tw = TextWrapper(width=100)
	out = []
	for ln in txt.splitlines():
		out.extend(tw.wrap(ln))
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

