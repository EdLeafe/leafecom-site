import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
import leafecom.model.meta as meta
import leafecom.lib.helpers as h
import leafecom.model as model

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)


class DlsController(BaseController):

	def index(self, id=None):
		c.section = None
		if id:
			sectionDict = {"vfp": "v", "python": "p", "dabo": "b", "osx": "x", "cb": "c", 
					"fox": "f", "taskpane": "t", "reportlistener": "r"}
			nameDict = {"vfp": "Visual FoxPro", "python": "Python", "dabo": "Dabo", "osx": "OS X", 
					"cb": "Codebook", "fox": "FoxPro 2.x", "taskpane": "Taskpane", "reportlistener": "ReportListener"}
			c.section = sectionDict.get(id, "o")
			c.sectionName = nameDict.get(id, "Other")
			q = model.meta.Session.query(model.Download)
			q = q.filter_by(ctype=c.section)
			q = q.filter_by(lpublish=1)
			c.downloads = q.all()
		return render("dls.html")
