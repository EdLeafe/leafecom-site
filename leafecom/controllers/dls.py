import datetime
import decimal
import logging
import os
import shutil
import smtplib
import stat
import time

from sqlalchemy import desc
from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect
from pylons.decorators.rest import restrict
import six

from leafecom.lib.base import BaseController, render
import leafecom.lib.helpers as h
import leafecom.model as model
import leafecom.model.meta as meta


log = logging.getLogger(__name__)


class DlsController(BaseController):
    def index(self, id=None):
        c.section = None
        if id:
            sectionDict = {"vfp": "v", "python": "p", "dabo": "b", "osx": "x", "cb": "c", 
                    "fox": "f", "taskpane": "t", "reportlistener": "r"}
            nameDict = {"vfp": "Visual FoxPro", "python": "Python", "dabo": "Dabo", "osx": "OS X", 
                    "cb": "Codebook", "fox": "FoxPro 2.x", "taskpane": "Taskpane", "reportlistener": "ReportListener"}
            c.section = unicode(sectionDict.get(id, "o"))
            c.sectionName = nameDict.get(id, "Other")
            q = meta.Session.query(model.Download)
            q = q.filter_by(ctype=c.section)
            q = q.filter_by(lpublish=1)
            q = q.order_by(desc("dlastupd"))
            c.downloads = self._query_all(q)
        return render("dls.html")


    def upload(self):
        c.filename = ""
        return render ("upload.html")


    @h.retry_lost
    def _query_all(self, query):
        return query.all()


    @restrict("POST")
    def upload_file(self):
        post = request.POST
        newfile = post.get("newfile")
        try:
            newname = newfile.filename
        except AttributeError:
            # Will happen if newfile is None
            abort(400, "No file specified")
        target_file = os.path.join("/var/www/uploads", newfile.filename.replace(os.sep, "_"))

        with file(target_file, "wb") as file_obj:
                    shutil.copyfileobj(newfile.file, file_obj)
        newfile.file.close()
        file_size = os.stat(target_file)[stat.ST_SIZE]
        kbytes = file_size / 1024.0
        if kbytes > 1000:
            fsize = "%.1fMB" % (kbytes / 1024.0)
        else:
            fsize = "%.1fK" % kbytes
        # Don't use the CDN; use the generic download URL that will redirect.
        cdnBase = "http://c118811.r11.cf0.rackcdn.com"
        dlBase = "http://leafe.com/download"
        fldr = {"c": "cb", "d": "dabo"}.get(post["file_section"], "")
        cfile = os.path.join(dlBase, fldr, newfile.filename)

        dl = model.Download()
        dl.ctype = post["file_section"]
        dl.ctitle = post["file_title"]
        dl.mdesc = post["file_descrip"]
        dl.cfile = cfile
        dl.ccosttype = post["file_license"]
        dl.ncost = decimal.Decimal(post["file_cost"])
        dl.csize = six.text_type(fsize)
        dl.cauthor = post["file_author"]
        dl.cauthoremail = post["file_email"]
        dl.dlastupd = datetime.date.today()
        dl.lpublish = False

        @h.retry_lost
        def _add_dl_model():
            model.meta.Session.add(dl)
            model.meta.Session.commit()

        _add_dl_model()

        body = """Originating IP = %s
Section = %s
Title = %s
File = %s
License = %s
Cost = %s
Size = %s
Author = %s
Email = %s

Description:
%s
""" % (request.remote_addr, dl.ctype, dl.ctitle, dl.cfile, dl.ccosttype, dl.ncost,
        dl.csize, dl.cauthor, dl.cauthoremail, dl.mdesc)

        msg = """From: File Uploads <files@leafe.com>
X-Mailer: pylons script
To: Ed Leafe <ed@leafe.com>
Subject: New Uploaded File
Date: %s

%s
""" % (time.strftime("%c"), body)
        smtp = smtplib.SMTP("mail.leafe.com")
        smtp.sendmail("files@leafe.com", "ed@leafe.com", msg)

        c.filename = newfile.filename
        c.filesize = fsize
        c.email = dl.cauthoremail
        return render("upload.html")
