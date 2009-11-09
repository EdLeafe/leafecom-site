import smtplib
import re
import random
import datetime
import time
import logging

from sqlalchemy import or_, and_, desc
from sqlalchemy.orm.exc import NoResultFound
from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
import webhelpers.paginate as paginate
import leafecom.model.meta as meta
import leafecom.lib.helpers as h
import leafecom.model as model
Archive = model.Archive

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)


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
		return self._showMessage()


	def byMID(self, listname, id):
		modelSession = model.meta.Session
		query = modelSession.query(Archive)
		query = query.filter_by(cmessageid=id)
		try:
			c.message = query.one()
		except NoResultFound:
			return "Sorry, no message matches that ID"
		return self._showMessage()


	def reportAbuse(self, id):
		modelSession = model.meta.Session
		query = modelSession.query(Archive)
		query = query.filter(Archive.cmessageid == id)
		try:
			msg = query.one()
		except NoResultFound:
			return "Sorry, no message matches that ID"
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
Message: http://leafe.com/archives/showMsg/%s
Reporting IP: %s

Email content:
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

%s
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
""" % (id, msgNum, reporting_ip, text)
		server = smtplib.SMTP("localhost")
		server.sendmail(frmAddr, toAddr,
				"To: Ed Leafe <ed@leafe.com>\nSubject: %s\n\n%s" % (subj, mailMsg))
		server.quit()
		return "<h2>Your report has been added, and will be reviewed.</h2>"


	def _showMessage(self):
		c.maskedFrom = self._maskEmail(c.message.cfrom)
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
#		subjectPhraseRequired 	'subj phrase' 
# 		orderBy							 	'dtDesc' 
# 		startDay 							'0' 
# 		startMonth					 	'0' 
# 		startYear 							'0' 
# 		endDay				 				'0' 
# 		endMonth 						'0' 
# 		endYear 							'0' 
# 		btnSubmit						'   Search!   ' 
#		batchSize							'50'

	def results(self, id=None):
# 		if request.method != "POST":
# 			# Returning from the paginator
# 			return "%s" % session["query"]
# 			c.paginator.page = int(request.params.get("page", 1))
# 			return render("/archive_results.html")

		# Extract the values submitted, or use the cached session.
		def safeGet(nm, cast=None):
			failFlag = "%^%^%^^^%^%^%^%^^"
			ret = request.params.get(nm, failFlag)
			if ret == failFlag:
				try:
					ret = session[nm]
				except KeyError:
					ret = None
			else:
				session[nm] = ret
				session.save()
			if cast and ret is not None:
				ret = cast(ret)
			return ret
			
		c.listname = safeGet("listname")
		authorRequired = safeGet("authorRequired")
		phraseRequired = safeGet("phraseRequired")
		cList = safeGet("cList")
		wordsForbidden = safeGet("wordsForbidden")
		wordsRequired = safeGet("wordsRequired")
		dateRange = safeGet("dateRange")
		subjectPhraseRequired = safeGet("subjectPhraseRequired")
		orderBy = safeGet("orderBy")
		startDay = safeGet("startDay", int)
		startMonth = safeGet("startMonth", int)
		startYear = safeGet("startYear", int)
		endDay = safeGet("endDay", int)
		endMonth = safeGet("endMonth", int)
		endYear = safeGet("endYear", int)
		btnSubmit = safeGet("btnSubmit")
		batchSize = int(safeGet("batchSize"))
		# The checkboxes work differently. First, see if there are the normal
		# fields for a form submission
		isForm = "btnSubmit" in request.params
		log.critical("HAS SUBMIT: " + str(isForm))
		if isForm:
			chkNF = request.params.get("chkNF")
			chkOT = request.params.get("chkOT")
		else:
			# Use the session cache
			try:
				chkNF = session["chkNF"]
			except KeyError:
				chkNF = ""
			session["chkNF"] = chkNF
			try:
				chkOT = session["chkOT"]
			except KeyError:
				chkOT = ""
			session["chkOT"] = chkOT
			session.save()
		
		log.critical("NF: %s" % chkNF)
		log.critical("OT: %s" % chkOT)
		
		modelSession = model.meta.Session
		query = modelSession.query(Archive)
		query = query.filter_by(clist=self._listAbbreviation(c.listname))

		# Date range
		today = datetime.date.today()
		tomorrow = today + datetime.timedelta(1)
		if dateRange != "dtAll":
			if dateRange == "dtToday":
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
				start = datetime.date(startYear, startMonth, startDay)
				if (not endYear) or (not endMonth) or (not endDay):
					end = tomorrow
				else:
					end = datetime.date(int(endYear), int(endMonth), int(endDay))
			query = query.filter("tposted>=:start and tposted<:end").params(start=start, end=end)

		if authorRequired:
			authComp = "%%%s%%" % authorRequired
			query = query.filter(model.archive_table.c.cfrom.like(authComp))
		if phraseRequired:
			query = query.filter(model.archive_table.c.mtext.like(authComp))
		if subjectPhraseRequired:
			query = query.filter(model.archive_table.c.subject.like(subjectPhraseRequired))
		
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
		c.currentPage = int(request.params.get("page", 1))
		c.firstMsgOffset = batchSize * (c.currentPage-1)
		c.paginator = paginate.Page(query,
				page=c.currentPage,
				items_per_page=batchSize)
		elapsed = time.time() - startTime
		c.elapsed = "%.4f" % elapsed
		
		return render("/archive_results.html")


	def _properListName(self, val):
		return {"profox": "ProFox", "prolinux": "ProLinux", "propython": "ProPython", 
				"valentina": "Valentina", "codebook": "Codebook", "dabo-dev": "Dabo-Dev", 
				"dabo-users": "Dabo-Users"}.get(val, "")


	def _listAbbreviation(self, val):
		return {"profox": "p", "prolinux": "l", "propython": "y", "valentina": "v", "codebook": "c", 
				"dabo-dev": "d", "dabo-users": "u"}.get(val, "")


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


	def _maskEmail(self, val):
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


	def _processMsg(self, rec):
		msg = rec.mtext.strip()
		msg = self._maskEmail(msg)
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
		