import email
import base64
import quopri
import smtplib
import re
import random
import datetime
import time
import math
import logging

from sqlalchemy import or_, and_, desc
from sqlalchemy.orm.exc import NoResultFound
from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify
import leafecom.model.meta as meta
import leafecom.lib.helpers as h
import leafecom.model as model
Archive = model.Archive

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

oneDay = datetime.timedelta(1)

class ArchivesController(BaseController):
	SPC_HOLDER = "~~~"

	def index(self):
		if request.params:
			return str(request.params)
		c.listname = c.properListName = ""
		c.searchOK = True
		return render("/archives.html")


	def search(self, id=None):
		c.listname = id
		c.searchOK = True
		c.properListName = self._properListName(id)
		return render("/archives.html")


	def msg(self, id):
		modelSession = model.meta.Session
		query = modelSession.query(Archive)
		query = query.filter_by(imsg=id)
		c.message = query.first()
		if c.message is None:
			abort(404, "No message with id=%s exists" % id)
		c.listname = session.get("listname", "")
		try:
			msgIDs = [res.imsg for res in session["fullresults"]]
		except KeyError:
			msgIDs = []
		c.priorLink = ""
		c.nextLink = ""
		c.fullThreadLink = "/archives/full_thread/%s" % c.message.imsg
		try:
			thisPos = msgIDs.index(c.message.imsg)
		except ValueError:
			thisPos = None
		if thisPos is not None:
			if thisPos > 0:
				priorMsg = msgIDs[thisPos - 1]
				c.priorLink = "/archives/msg/%s" % priorMsg
			try:
				nextMsg = msgIDs[thisPos + 1]
				c.nextLink = "/archives/msg/%s" % nextMsg
			except IndexError:
				# This is the last message
				pass
		return self._showMessage()


	def decode_message(self, id):
		msgid = str(id)	#request.parameters.get("msgnum")
		modelSession = model.meta.Session
		query = modelSession.query(Archive)
		query = query.filter_by(imsg=msgid)
		rec = query.first()
		txt = rec.mtext
#		try:
#			decoded = base64.b64decode(txt)
#		except TypeError:
#			# Not b64 encoded
#			decoded = txt
		decoded = txt
		# Get rid of quoted-printable, if any
		final = quopri.decodestring(decoded)
		rec.mtext = final
		modelSession.flush()
		redirect_to("/archives/msg/%s" % msgid)
		

	def byMID(self, id):
		modelSession = model.meta.Session
		query = modelSession.query(Archive)
		query = query.filter_by(cmessageid=id)
		try:
			message = query.one()
		except NoResultFound:
			return "Sorry, no message matches that ID"
		redirect_to(controller="archives", action="msg", id=message.imsg)


	def reportAbuse(self, url):
		modelSession = model.meta.Session
		query = modelSession.query(Archive)
		query = query.filter(Archive.cmessageid == url)
		try:
			msg = query.one()
		except NoResultFound:
			return "Sorry, no message matches that mesage ID"
		msgNum = msg.imsg
		text = msg.mtext
		cfrom = msg.cfrom
		reporting_ip = request.remote_addr
		# Need to create the model for the abuse table
		#context.addToAbuse(cmessageid=msgID, cfrom=cfrom, reporting_ip= reporting_ip)

		# Send me an email so that I know if a bogus ad has been submitted
		toAddr = "ed@leafe.com"
		frmAddr = "techAbuse@leafe.com"
		subj = "ProFoxTech Abuse"
		mailMsg = """

@@@@@@@@@@@
MessageID: %s
Message: http://leafe.com/archives/msg/%s
Reporting IP: %s

Email content:
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

%s
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
""" % (url, msgNum, reporting_ip, text)
		server = smtplib.SMTP("localhost")
		server.sendmail(frmAddr, toAddr,
				"To: Ed Leafe <ed@leafe.com>\nSubject: %s\n\n%s" % (subj, mailMsg))
		server.quit()
		return "<h2>Your report has been added, and will be reviewed.</h2>"


	def _showMessage(self):
		c.requestIP = request.remote_addr
		c.maskedFrom = h.maskEmail(c.message.cfrom)
		c.displayMessage = self._processMsg(c.message)
		c.copyYear = c.message.tposted.year
		c.copyName = c.message.cfrom.split("<")[0].strip().replace("\"", "")
		return render("/message.html")



############		Form Values				############
# 		authorRequired				"AUTHOR'S NAME" 
# 		phraseRequired 				'SPECIFIC PHRASE' 
# 		cList 								'profox' 
# 		wordsForbidden			 	'NOT APPEAR' 
# 		wordsRequired 				'MUST APPEAR' 
# 		dateRange 						'dtLastWeek'
# 		startDate 						'2010.04.20'
# 		endDate 						'2010.04.28'
#		subjectPhraseRequired 	'subj phrase' 
# 		orderBy							 	'dtDesc' 
# 		btnSubmit						'   Search!   ' 
#		batchSize							'50'
##### NO LONGER USED ##################
# 		startDay 							'0' 
# 		startMonth					 	'0' 
# 		startYear 							'0' 
# 		endDay				 				'0' 
# 		endMonth 						'0' 
# 		endYear 							'0' 
######################################

	def results(self, id=None):
		c.url = request.url
		if request.method != "POST":
			page = int(request.params.get("page", "1"))
			try:
				batchSize = session["batchSize"]
				c.total_pages = session["total_pages"]
				c.listname = session["listname"]
			except KeyError:
				abort(401, "No session found to display results")	
			page = max(1, page)
			page = min(page, c.total_pages)
			# Get the slice
			recStart = (batchSize * (page-1))
			recEnd = (batchSize * page) - 1
			allrecs = session["fullresults"]
			c.numResults = len(allrecs)
			c.elapsed = session["elapsed"]
			c.page = page
			c.results = allrecs[recStart:recEnd]
			return render("/archive_results.html")

		# Extract the values submitted
		prms = request.params
		
		c.params = prms
		
		c.listname = prms.get("listname")
		authorRequired = prms.get("authorRequired")
		phraseRequired = prms.get("phraseRequired")
		cList = prms.get("cList")
		wordsForbidden = prms.get("wordsForbidden")
		wordsRequired = prms.get("wordsRequired")
		dateRange = prms.get("dateRange")
		subjectPhraseRequired = prms.get("subjectPhraseRequired")
		orderBy = prms.get("orderBy")
		startDate = prms.get("startDate")
		if startDate == "START":
			# Didn't get changed
			startDate = "1990.01.01"
		endDate = prms.get("endDate")
		if endDate == "END":
			# Didn't get changed
			endDate = datetime.date.today().strftime("%Y.%m.%d")
# 		startDay = int(prms.get("startDay"))
# 		startMonth = int(prms.get("startMonth"))
# 		startYear = int(prms.get("startYear"))
# 		endDay = int(prms.get("endDay"))
# 		endMonth = int(prms.get("endMonth"))
# 		endYear = int(prms.get("endYear"))
		btnSubmit = prms.get("btnSubmit")
		batchSize = int(prms.get("batchSize"))
		chkNF = prms.get("chkNF")
		chkOT = prms.get("chkOT")
		# Save the results
		session["listname"] = c.listname
		session["authorRequired"] = authorRequired
		session["phraseRequired"] = phraseRequired
		session["cList"] = cList
		session["wordsForbidden"] = wordsForbidden
		session["wordsRequired"] = wordsRequired
		session["dateRange"] = dateRange
		session["subjectPhraseRequired"] = subjectPhraseRequired
		session["orderBy"] = orderBy
		session["startDate"] = startDate
		session["endDate"] = endDate
# 		session["startDay"] = startDay
# 		session["startMonth"] = startMonth
# 		session["startYear"] = startYear
# 		session["endDay"] = endDay
# 		session["endMonth"] = endMonth
# 		session["endYear"] = endYear
		session["btnSubmit"] = btnSubmit
		session["batchSize"] = batchSize
		session["chkNF"] = chkNF
		session["chkOT"] = chkOT
		session.save()

		modelSession = model.meta.Session
		query = modelSession.query(Archive)
		query = query.filter_by(clist=self._listAbbreviation(c.listname))

		# Date range
		today = datetime.date.today()
		tomorrow = today + datetime.timedelta(1)
		if dateRange != "dtAll":
			if dateRange == "dtLastYear":
				start = today.replace(year=today.year-1)
				end = tomorrow
			elif dateRange == "dtToday":
				start = today
				end = tomorrow
			elif dateRange == "dtYesterday":
				start = today - datetime.timedelta(1)
				end = today
			elif dateRange == "dtLastWeek":
				start = today - datetime.timedelta(7)
				end = tomorrow
			elif dateRange == "dtLastMonth":
				start = today - datetime.timedelta(30)
				end = tomorrow
			else:
				# Custom date
				startYear, startMonth, startDay = [int(part) for part in startDate.split(".")]
				endYear, endMonth, endDay = [int(part) for part in endDate.split(".")]
				start = datetime.date(startYear, startMonth, startDay)
				end = datetime.date(int(endYear), int(endMonth), int(endDay)) + oneDay

			query = query.filter("tposted>=:start and tposted<:end").params(start=start, end=end)

		if authorRequired:
			authComp = "%%%s%%" % authorRequired
			query = query.filter(model.archive_table.c.cfrom.like(authComp))
		if phraseRequired:
			phraseComp = "%%%s%%" % phraseRequired
			query = query.filter(model.archive_table.c.mtext.like(phraseComp))
		if subjectPhraseRequired:
			subjPhraseComp = "%%%s%%" % subjectPhraseRequired
			query = query.filter(model.archive_table.c.csubject.like(subjPhraseComp))

		if c.listname == "profox":
			if chkNF != "on":
				query = query.filter(model.archive_table.c.csubject.op("not regexp")('[ [:punct:]]NF[ [:punct:]]'))
			if chkOT != "on":
				query = query.filter(model.archive_table.c.csubject.op("not regexp")('[ [:punct:]]OT[ [:punct:]]'))

		matchByWordClause = goodClause = badClause = ""
		if wordsRequired:
			required = self._cleanSpaces(wordsRequired).split()
			goodWords = ["+" + self._restoreSpaces(wd).replace("'", "\\'")
					for wd in required if wd]
			goodClause += " ".join(goodWords)
		if wordsForbidden:
			forbidden = self._cleanSpaces(wordsForbidden).split()
			badWords = ["-" + self._restoreSpaces(wd).replace("'", "\\'")
					for wd in forbidden if wd]
			badClause += " ".join(badWords)
		matchByWordClause = (" ".join((goodClause, badClause))).strip()
		if matchByWordClause:
			query = query.filter(" match (mtext) against (:words IN BOOLEAN MODE) ").params(words=matchByWordClause)
		
		orderByTemplate = " ORDER BY %s "
		if orderBy == "dtDesc":
			query = query.order_by(desc("tposted"))
		elif orderBy == "dtAsc":
			query = query.order_by("tposted")
		elif orderBy == "author":
			query = query.order_by("cfrom")
		elif orderBy == "subject":
			# Add the equivalent of 'puresubject'?
			query = query.order_by("csubject")

		startTime = time.time()
		session["fullresults"] = allrecs = query.all()
		session["elapsed"] = c.elapsed = "%.4f" % (time.time() - startTime)
		c.numResults = len(allrecs)
		
		page = int(request.params.get("page", "1"))
		session["total_pages"] = c.total_pages = int(math.ceil(float(c.numResults) / batchSize))
		page = min(page, c.total_pages)
		session.save()
		
		# Get the slice
		recStart = (batchSize * (page-1))
		recEnd = (batchSize * page) - 1
		c.page = page
		c.results = allrecs[recStart:recEnd]
		return render("/archive_results.html")


	def _properListName(self, val):
		return {"profox": "ProFox", "prolinux": "ProLinux", "propython": "ProPython", 
				"valentina": "Valentina", "codebook": "Codebook", "dabo-dev": "Dabo-Dev", 
				"dabo-users": "Dabo-Users"}.get(val, "")


	def _listAbbreviation(self, val):
		return {"profox": u"p", "prolinux": u"l", "propython": u"y", "valentina": u"v", "codebook": u"c", 
				"dabo-dev": u"d", "dabo-users": u"u"}.get(val, "")


	def _cleanSpaces(self, strVal):
		# Go along the string, and if we are between double quotes, replace any 
		# spaces with the space holder
		ret = []
		inQuote = False
		for ch in strVal:
			if ch == " ":
				if inQuote:
					ch = self.SPC_HOLDER
			else:
				if ch == "\"":
					inQuote = not inQuote
			ret.append(ch)
		return "".join(ret)
	

	def _restoreSpaces(self, strVal):
		return strVal.replace(self.SPC_HOLDER, " ")


	def _processMsg(self, rec):
		msg = rec.mtext.strip()
		c.messagelength = len(msg)
# 		try:
# 			msg = email.base64mime.decodestring(msg)
# 		except Exception:
# 			# Not base64 encoded
# 			pass
# 		msg = email.quoprimime.decode(msg)
		msg = h.maskEmail(msg)
		if msg.lower().endswith("</html>"):
			# This is HTML
			hilite = False
		else:
			hilite = True
			# Replace angled brackets with escaped forms
#			msg = msg.replace("<", "&lt;").replace(">", "&gt;")
			# Change the newlines
#			msg = msg.replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")
		return msg


	def full_thread(self, id):
		modelSession = model.meta.Session
		c.listname = session.get("listname", "")
		query = modelSession.query(Archive)
		query = query.filter_by(imsg=id)
		
		msg = query.first()
		msgTime = msg.tposted
		startPeriod = msgTime - datetime.timedelta(90)
		subj = msg.csubject
		listabbr = msg.clist
		
		pat = re.compile(r"\bre: *", re.I)
		subj = pat.sub("", subj)
# 		pat = re.compile(r"[\{\[]ot[\{\]] *", re.I)
# 		subj = pat.sub("", subj)
# 		pat = re.compile(r"[\{\[]nf[\{\]] *", re.I)
# 		subj = pat.sub("", subj)
# 		pat = re.compile(r"[\{\[]admin[\{\]] *", re.I)
# 		subj = pat.sub("", subj)
		subj = "%%%s%%" % subj

		query = modelSession.query(Archive)
		query = query.filter_by(clist=listabbr)
		query = query.filter("tposted>=:start").params(start=startPeriod)
		query = query.filter(model.archive_table.c.csubject.like(subj))
		query = query.order_by("tposted")
		c.results = query.all()
		
		return render("/full_thread.html")
