import logging
import datetime

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render
import leafecom.model.meta as meta
import leafecom.lib.helpers as h
import leafecom.model as model
MedData = model.MedData

log = logging.getLogger(__name__)
today = datetime.date.today()


class MedicalController(BaseController):
	def index(self):
		c.reccount = meta.Session.query(MedData).count()
		return render("medical_entry.html")


	def data_entry(self):
		rp = request.params
		dt = rp.get("date_taken", today).strftime("%Y-%m-%d")
		wt = rp.get("weight")
		syst = rp.get("systolic")
		dias = rp.get("diastolic")
		data = MedData()
		data.date_taken = dt
		data.weight = wt
		data.systolic = syst
		data.diastolic = dias
		session = model.meta.Session
		session.save(data)
		session.flush()

		return self.index()
