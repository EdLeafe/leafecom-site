import logging
import sqlite3
import datetime
import os

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class VaultController(BaseController):

    def index(self, key, id):
		t = datetime.date.today()
		kv = t.year + t.month + t.day
		kv2 = kv - 2000
		if not int(key) in (kv, kv2):
			abort(403)
		pth = "/home/ed/pylons/leafe.com/leafecom/lib/xpw.db"
		db = sqlite3.connect(pth)
		crs = db.cursor()
		search = "%%%s%%" % id 
		sql = """ 
		select pkid, site, user, pw, email, misc
		from pw
		where (site like ?)
		or (misc like ?) """
		crs.execute(sql, (search, search))
		c.data = crs.fetchall()
		return render("/vault.html")

