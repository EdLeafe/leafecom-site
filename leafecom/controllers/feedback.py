import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render
import leafecom.model.meta as meta
import leafecom.lib.helpers as h
import leafecom.model as model
Feedback = model.Feedback

log = logging.getLogger(__name__)


class FeedbackController(BaseController):
	def index(self):
		params = request.params
		action = params.get("action", "no action")
		c.src = params.get("src", "no source")
		c.campaign = params.get("campaign", "no campaign")
		c.comment = params.get("comment", "Cool!")
		if action != "ok":
			return render("/feedback.html")
		modelSession = model.meta.Session
		fb = Feedback()
		fb.src = c.src
		fb.campaign = c.campaign
		fb.comment = c.comment
		modelSession.save(fb)
		modelSession.commit()

		return "<h3>Thanks for your feedback!</h3> Comment Length: %s" % len(c.comment)
