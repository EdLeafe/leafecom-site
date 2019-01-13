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

import elasticsearch
from sqlalchemy import or_, and_, desc
from sqlalchemy import text as sqltext
from sqlalchemy.orm.exc import NoResultFound
from pylons import request, response, session, url, tmpl_context as c
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
import leafecom.model.meta as meta
import leafecom.lib.helpers as h
import leafecom.model as model
Archive = model.Archive

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

oneDay = datetime.timedelta(1)

es_client = elasticsearch.Elasticsearch(host="dodb")
# My original names in the DB suck, so...
DB_TO_ELASTIC_NAMES = {
        "imsg": "msg_num",
        "clist": "list_name",
        "csubject": "subject",
        "cfrom": "from",
        "tposted": "posted",
        "cmessageid": "message_id",
        "creplytoid": "replyto_id",
        "mtext": "body",
        "id": "id",
        }
ELASTIC_TO_DB_NAMES = {v: k for k, v in DB_TO_ELASTIC_NAMES.items()}


def extract_records(resp, translate_to_db=True):
    recs = [r["_source"] for r in resp["hits"]["hits"]]
    excepts = 0
    for rec in recs:
        try:
            rec["posted"] = datetime.datetime.strptime(
                    rec["posted"], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            rec["posted"] = datetime.datetime.strptime(
                    rec["posted"], "%Y-%m-%d %H:%M:%S")
            excepts += 1
    if translate_to_db:
        allrecs = [h.DotDict(rec) for rec in db_names_from_elastic(recs)]
    else:
        allrecs = recs
    c.date_excepts = excepts
    return allrecs


def get_sort_order(order_by):
    return {"dtDesc": "posted:desc",
            "dtAsc": "posted:asc",
            "author": "from:asc",
            "subject": "subject:asc"}.get(order_by)


def db_names_from_elastic(recs):
    return [dict((ELASTIC_TO_DB_NAMES.get(k), v)
            for k,v in rec.items()) for rec in recs]


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


    def msg(self, id=None):
        if id is None:
            abort(400, "Sorry, a message ID is required.")
        c.from_developer = request.remote_addr == h.get_sa_home_ip()
        if c.from_developer:
            kwargs = {"body": {"query": {"match": {"msg_num": id}}}}
            resp = es_client.search("email", doc_type="mail", **kwargs)
            allrecs = extract_records(resp)
            if not allrecs:
                abort(404, "No message with id=%s exists" % id)
            c.message = allrecs[0]
            c.session = session
        else:
            modelSession = model.meta.Session
            query = modelSession.query(Archive)
            query = query.filter_by(imsg=id)
            try:
                c.message = self._query_first(query)
            except NoResultFound:
                abort(404, "No message with id=%s exists" % id)
        c.listname = session.get("listname", "")
        try:
            msgIDs = session["fullresults"]
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
        msgid = str(id)    #request.parameters.get("msgnum")
        modelSession = model.meta.Session
        query = modelSession.query(Archive)
        query = query.filter_by(imsg=msgid)
        try:
            c.message = self._query_first(query)
        except NoResultFound:
            abort(404, "No message with id=%s exists" % id)
        txt = rec.mtext
#        try:
#            decoded = base64.b64decode(txt)
#        except TypeError:
#            # Not b64 encoded
#            decoded = txt
        decoded = txt
        # Get rid of quoted-printable, if any
        final = quopri.decodestring(decoded)
        rec.mtext = final
        modelSession.flush()
        redirect("/archives/msg/%s" % msgid)


    def byMID(self, id=None):
        if id is None:
            abort(400, "Sorry, a message ID is required.")
        modelSession = model.meta.Session
        query = modelSession.query(Archive)
        query = query.filter_by(cmessageid=id)
        try:
            message = self._query_first(query)
        except NoResultFound:
            modelSession.rollback()
            abort(404, "No message with id=%s exists" % id)
        if not message:
            return "Sorry, no message matches that ID"
        redirect(url(controller="archives", action="msg", id=message.imsg))


    def reportAbuse(self, url):
        # Added 2012.09.17 because this seems to be a google bot.
        # Added 2013.01.06: getting a lot of abuse reports from IPs beginning
        #    with 74.125.18[67]
        bad_pat = re.compile(r"74.125.18\d.\d{1,3}")
        reporting_ip = request.remote_addr
        if reporting_ip == "66.249.73.138" or bad_pat.match(reporting_ip):
            log.info("Abuse bot detected; ip=%s" % reporting_ip)
            return "Sorry, you seem to be a bot."

        def prove_it(wrong=False):
            f1 = random.randint(1, 8)
            f2 = random.randint(1, 8)
            log.warn("WRONG: %s" % wrong)
            c.wrong = wrong
            c.question = "How much is %s + %s?" % (f1, f2)
            c.expected = f1 + f2
            c.url = url
            return render("/human.html")

        modelSession = model.meta.Session
        proof_answer = request.params.get("answer")
        if proof_answer is None:
            # Make sure this is a human
            return prove_it()
        expected = request.params.get("expected")
        if not expected == proof_answer:
            return prove_it(wrong=True)

        query = modelSession.query(Archive)
        query = query.filter(Archive.cmessageid == url)
        try:
            msg = self._query_first(query)
        except NoResultFound:
            modelSession.rollback()
            abort(404, "No message with id=%s exists" % id)
        msgNum = msg.imsg
        text = msg.mtext
        cfrom = msg.cfrom

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
        mailMsg = mailMsg.encode("utf8")
        server = smtplib.SMTP("localhost")
        server.sendmail(frmAddr, toAddr,
                "To: Ed Leafe <ed@leafe.com>\nSubject: %s\n\n%s" % (subj, mailMsg))
        server.quit()
        return "<h2>Your report has been added, and will be reviewed.</h2>"


    def _showMessage(self):
        c.requestIP = request.remote_addr
        c.maskedFrom = h.maskEmail(c.message.cfrom)
#        c.maskedFrom = c.message.cfrom
        c.displayMessage = self._processMsg(c.message)
        c.copyYear = c.message.tposted.year
        c.copyName = c.message.cfrom.split("<")[0].strip().replace("\"", "")
        return render("/message.html")



######  Form Values  ##############################
#         authorRequired         "AUTHOR'S NAME"
#         phraseRequired         'SPECIFIC PHRASE'
#         listname               'profox'
#         wordsForbidden         'NOT APPEAR'
#         wordsRequired          'MUST APPEAR'
#         dateRange              'dtLastWeek'
#         startDate              '2010.04.20'
#         endDate                '2010.04.28'
#         subjectPhraseRequired  'subj phrase'
#         orderBy                'dtDesc'
#         btnSubmit              '   Search!   '
#         batchSize              '50'
##### NO LONGER USED ##############################
#         cList                  'profox'
#         startDay               '0'
#         startMonth             '0'
#         startYear              '0'
#         endDay                 '0'
#         endMonth               '0'
#         endYear                '0'
###################################################


    def date_range(self, dateRange, startDate, endDate, fmt=False):
        # Date range
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(1)
        start = end = None
        if dateRange == "dtAll":
            start = datetime.date(1901, 1, 1)
            end = tomorrow
        elif dateRange == "dtLastYear":
            try:
                start = today.replace(year=today.year-1)
            except ValueError:
                # Should only happen on Feb. 29
                start = today - datetime.timedelta(1)
                start = start.replace(year=today.year-1)
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
            startYear, startMonth, startDay = [
                    int(part) for part in startDate.split(".")]
            endYear, endMonth, endDay = [
                    int(part) for part in endDate.split(".")]
            start = datetime.date(startYear, startMonth, startDay)
            end = datetime.date(int(endYear), int(endMonth),
                    int(endDay)) + oneDay
        if fmt:
            return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
        else:
            return start, end


    @staticmethod
    def add_match(lst, key, val, operator=None):
        if operator:
            lst.append({"match": {key: {"query": val, "operator": operator}}})
        else:
            lst.append({"match": {key: val}})


    @staticmethod
    def add_match_phrase(lst, key, val):
        lst.append({"match_phrase": {key: val}})


    def results(self, id=None):
        c.error_message = ""
        c.url = request.remote_addr
        c.from_developer = request.remote_addr == h.get_sa_home_ip()

        if request.method != "POST":
            page = int(request.params.get("page", "1"))
            try:
                batchSize = session["batchSize"]
                c.total_pages = session["total_pages"]
                c.listname = session["listname"]
            except KeyError:
                abort(403, "No session found to display results")
            page = max(1, page)
            page = min(page, c.total_pages)
            # Get the slice
            recStart = (batchSize * (page-1))
            recEnd = (batchSize * page) - 1
            if c.from_developer:
                c.session = session
                kwargs = {"body": session.get("query_body")}
                kwargs["sort"] = [get_sort_order(session.get("orderBy"))]
                kwargs["size"] = batchSize
                session.query_body = kwargs["body"]
                # Now run the query for real
                kwargs["size"] = batchSize
                kwargs["from_"] = recStart
                c.query_statement = str(kwargs)
                c.params = {}
                startTime = time.time()
                resp = es_client.search("email", doc_type="mail", **kwargs)
                session["elapsed"] = c.elapsed = "%.4f" % (
                        time.time() - startTime)
                c.numResults = len(session["fullresults"])
                allrecs = extract_records(resp)
                c.results = allrecs

            else:
                allrecs = session["fullresults"]
                c.results = allrecs[recStart:recEnd]
                c.numResults = len(allrecs)
            c.elapsed = session["elapsed"]
            c.page = page

            try:
                c.results[0].imsg
            except IndexError, e:
                # No results; ignore
                pass
            except AttributeError, e:
                c.error_message = "Your session information has been lost."
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
        btnSubmit = prms.get("btnSubmit")
        batchSize = int(prms.get("batchSize"))
        chkNF = "chkNF" in prms
        chkOT = "chkOT" in prms
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
        session["btnSubmit"] = btnSubmit
        session["batchSize"] = batchSize
        session["chkNF"] = chkNF
        session["chkOT"] = chkOT
        session.save()


        if c.from_developer:
            kwargs = {"body": {"query": {
                    "bool": {
                        "must": [],
                        "must_not": [],
                    }}}}
            bqbm = kwargs["body"]["query"]["bool"]["must"]
            neg_bqbm = kwargs["body"]["query"]["bool"]["must_not"]

            listabb = self._listAbbreviation(c.listname)
            self.add_match(bqbm, "list_name", listabb)

            words_req = wordsRequired
            if words_req:
                self.add_match(bqbm, "body", words_req, operator="and")

            words_forbidden = wordsForbidden
            if words_forbidden:
                self.add_match(neg_bqbm, "body", words_forbidden,
                        operator="and")

            body_phrase = phraseRequired
            if body_phrase:
                self.add_match_phrase(bqbm, "body", body_phrase)

            subject_phrase = subjectPhraseRequired
            if subject_phrase:
                self.add_match_phrase(bqbm, "subject", subject_phrase)

            author = authorRequired
            if author:
                expr = "*%s*" % author
                bqbm.append({"wildcard": {"from": expr}})
            start, end = self.date_range(dateRange, startDate, endDate,
                    fmt=True)
            bqbm.append({"range": {"posted": {"gte": start}}})
            bqbm.append({"range": {"posted": {"lte": end}}})

            if not chkOT:
                self.add_match(neg_bqbm, "subject", "[OT]")
            if not chkNF:
                self.add_match(neg_bqbm, "subject", "[NF]")

            sortorder = get_sort_order(orderBy)
            kwargs["sort"] = [sortorder]
            kwargs["size"] = batchSize

            startTime = time.time()
            c.query_statement = str(kwargs)
            session["query_body"] = kwargs["body"]

            # Get the total number of hits. This will return the total without
            # pulling all the data.
#            kwargs["size"] = 0
            kwargs["size"] =10000
            kwargs["_source"] = ["msg_num"]
            startTime = time.time()
            resp = es_client.search("email", doc_type="mail", **kwargs)
            msg_nums = [r["_source"]["msg_num"] for r in resp["hits"]["hits"]]
            c.numResults = resp["hits"]["total"]

            # Now run the query for real
            kwargs.pop("_source")
            kwargs["size"] = batchSize
            kwargs["from_"] = int(request.params.get("page", "0"))
            resp = es_client.search("email", doc_type="mail", **kwargs)
            session["elapsed"] = c.elapsed = "%.4f" % (time.time() - startTime)
            total = "{:,}".format(resp["hits"]["total"])
#            return "%s" % [r["_source"] for r in resp["hits"]["hits"]][0]
            allrecs = extract_records(resp)
            session["fullresults"] = [rec["imsg"] for rec in allrecs]
            c.session = session

        else:
            modelSession = model.meta.Session
            query = modelSession.query(Archive)
            query = query.filter_by(clist=self._listAbbreviation(c.listname))


            start, end = self.date_range(dateRange, startDate, endDate)
            query = query.filter(sqltext(u"tposted>=:start and tposted<:end")).params(start=start, end=end)

            if authorRequired:
                authComp = u"%%%s%%" % authorRequired
                query = query.filter(model.archive_table.c.cfrom.like(authComp))
            if phraseRequired:
                phraseComp = u"%%%s%%" % phraseRequired
                query = query.filter(model.archive_table.c.mtext.like(phraseComp))
            if subjectPhraseRequired:
                subjPhraseComp = u"%%%s%%" % subjectPhraseRequired
                query = query.filter(model.archive_table.c.csubject.like(subjPhraseComp))

            if c.listname == "profox":
                if not chkNF:
                    query = query.filter(model.archive_table.c.csubject.op("not regexp")(u'[ [:punct:]]NF[ [:punct:]]'))
                if not chkOT:
                    query = query.filter(model.archive_table.c.csubject.op("not regexp")(u'[ [:punct:]]OT[ [:punct:]]'))

            matchByWordClause = goodClause = badClause = u""
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
            matchByWordClause = (u" ".join((goodClause, badClause))).strip()
            if matchByWordClause:
                query = query.filter(u" match (mtext) against (:words IN BOOLEAN MODE) ").params(words=matchByWordClause)

            orderByTemplate = u" ORDER BY %s "
            if orderBy == "dtDesc":
                query = query.order_by(desc("tposted"))
            elif orderBy == "dtAsc":
                query = query.order_by("tposted")
            elif orderBy == "author":
                query = query.order_by("cfrom")
            elif orderBy == "subject":
                # Add the equivalent of 'puresubject'?
                query = query.order_by("csubject")

            c.query_statement = "SQL: %s" % query.with_labels().statement + " Start: %s" % start + " End: %s" % end + " List: %s" % cList

            startTime = time.time()
            allrecs = self._query_all(query)
            session["fullresults"] = [rec.imsg for rec in allrecs]
            c.numResults = len(allrecs)
            session["elapsed"] = c.elapsed = "%.4f" % (time.time() - startTime)
            # For compatibility with the elasticsearch version
            c.date_excepts = 0
            c.session = session

        # Common to both DB and Elasticsearch
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


    @staticmethod
    def _listAbbreviation(val):
        return {"profox": u"p", "prolinux": u"l", "propython": u"y",
                "valentina": u"v", "codebook": u"c", "testing": u"t",
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
#         try:
#             msg = email.base64mime.decodestring(msg)
#         except Exception:
#             # Not base64 encoded
#             pass
#         msg = email.quoprimime.decode(msg)

#        msg = h.maskEmail(msg)
        if msg.lower().endswith("</html>"):
            # This is HTML
            hilite = False
        else:
            hilite = True
            # Replace angled brackets with escaped forms
#            msg = msg.replace("<", "&lt;").replace(">", "&gt;")
            # Change the newlines
#            msg = msg.replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")
        return msg


    @h.retry_lost
    def _query_first(self, query):
        ret = query.first()
        if ret is None:
            raise NoResultFound
        return ret


    @h.retry_lost
    def _query_all(self, query):
        return query.all()


    def full_thread(self, id=None):
        msgnum = id
        if msgnum is None:
            abort(400, "Sorry, a message ID is required.")
        c.listname = session.get("listname", "")
        c.url = request.remote_addr
        c.from_developer = request.remote_addr == h.get_sa_home_ip()
        kwargs = {"body": {"query": {"match": {"msg_num": msgnum}}}}
        resp = es_client.search("email", doc_type="mail", **kwargs)
        recs = extract_records(resp, translate_to_db=False)
        if not recs:
            abort(404, "No message with id=%s exists" % msgnum)

        subj = recs[0]["subject"]
        pat = re.compile(r"^re: *", re.I)
        subj = pat.sub("", subj)
        kwargs = {"body": {"query": {"match_phrase" : {"subject" : subj}}},
                "sort": ["posted:asc"]}
        resp = es_client.search("email", doc_type="mail", **kwargs)
        c.results = extract_records(resp, translate_to_db=True)
        c.query_statement = kwargs
        return render("/full_thread.html")






        modelSession = model.meta.Session
        c.error_message = ""
        c.listname = session.get("listname", "")
        c.url = request.remote_addr
        c.from_developer = request.remote_addr == h.get_sa_home_ip()
        query = modelSession.query(Archive)
        query = query.filter_by(imsg=id)
        try:
            msg = self._query_first(query)
        except NoResultFound:
            abort(404, "No message with id=%s exists" % id)
        try:
            msgTime = msg.tposted
        except AttributeError, e:
            # No message match the subject
            log.warn("Full thread failed for id=%s" % id)
            c.results = []
            return render("/archive_results.html")
        startPeriod = msgTime - datetime.timedelta(90)
        subj = msg.csubject.replace("\n", "  ").replace("\r", "")
        listabbr = unicode(msg.clist)

        pat = re.compile(r"^re: *", re.I)
        subj = pat.sub("", subj)
        subj = "%%%s%%" % subj

        query = modelSession.query(Archive)
        query = query.filter_by(clist=listabbr)
        query = query.filter(sqltext("tposted>=:start")).params(start=startPeriod)
        query = query.filter(model.archive_table.c.csubject.like(subj))
        query = query.order_by("tposted")
        c.results = self._query_all(query)
        c.query_statement = "SQL: %s" % query.with_labels().statement + " Subj: %s" % subj + " Period: %s" % startPeriod
        return render("/full_thread.html")
