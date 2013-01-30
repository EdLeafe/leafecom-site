import json
import logging
import os
from subprocess import Popen, PIPE
import tempfile

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)


class AddaliasController(BaseController):
	def __init__(self, *args, **kwargs):
		super(AddaliasController, self).__init__(*args, **kwargs)
		self.fname = "/etc/aliases"
		self.fulltext = file(self.fname).read()
		self.user_sep = "### USERS ###"
		self.direct_sep = "### DIRECT ###"
		self.user_alias_pattern = "ed-%s: ed"
		self.web_alias_pattern = "web-%s: ed"
		self.direct_alias_pattern = "%s: ed"


	def index(self, id=None):
		mthd = request.method
		self._returnHTML = ("html" in request.headers["Accept"])
		if mthd == "DELETE":
			return self._delAlias(id)

		prefix = request.headers.get("Prefix", "ed")
		if prefix == "None":
			# Direct alias
			self.aliasPattern = self.direct_alias_pattern
			self.sep = self.direct_sep
		else:
			self.aliasPattern = self.user_alias_pattern
			self.sep = self.user_sep
		self.sections = self.fulltext.split(self.sep)

		if id:
			return self._addAlias(id)
		c.mailnames = self.sections[1].strip().splitlines()
		c.post = request.POST
		if c.post:
			aliasToDelete = c.post.get("delalias", "")
			aliasToAdd = c.post.get("newalias", "")
			if aliasToAdd:
				return self._addAlias(aliasToAdd)
			else:
				return self._delAlias(aliasToDelete)
		else:
			c.mailnames.sort()
			return render("addalias.html")

	
	def search(self, term):
		user_lines = self.fulltext.split(self.user_sep)[1]
		direct_lines = self.fulltext.split(self.direct_sep)[1]
		web_lines = "\n".join([ln for ln in self.fulltext.splitlines()
				if ln.startswith("web-")])
		alias_lines = user_lines + direct_lines + web_lines
		mtchs = [ln.split(":")[0] for ln in alias_lines.splitlines()
				if (term in ln)]
		return json.dumps(mtchs)


	def _addAlias(self, nm):
		mailnames = self.sections[1].strip().splitlines()
		newalias = self.aliasPattern % nm
		mailnames.append(newalias)
		self._writeNewAliasFile(mailnames)
		ret = "Alias %s added" % nm
		if self._returnHTML:
			ret = "<h2>%s</h2>" % ret
		return ret

	
	def _delAlias(self, nm):
		alias_lines = self.fulltext.strip().splitlines()
		found = ""
		for pat in (self.user_alias_pattern, self.web_alias_pattern,
				self.direct_alias_pattern):
			delalias = pat % nm
			try:
				alias_lines.remove(delalias)
				found = delalias.split(":")[0]
				break
			except ValueError:
				continue
		if not found:
			return "No such alias: %s" % delalias.split(":")[0]
		txt = "\n".join(alias_lines)
		self._writeNewAliasFile(None, txt)
		ret = "Alias %s deleted" % found
		if self._returnHTML:
			ret = "<h2>%s</h2>" % ret
		return ret


	def _writeNewAliasFile(self, mailnames, new_text=None):
		if new_text is None:
			# remove dupes
			mailnames = list(set(mailnames))
			mailnames.sort()
			updated_names = "\n".join(mailnames)
			section_text = "\n%s\n%s\n%s\n" % (self.sep, updated_names, self.sep)
			new_text = "\n".join([self.sections[0].strip(), section_text,
					self.sections[2].lstrip()])
		fd, nm  = tempfile.mkstemp()
		os.close(fd)
		file(nm, "w").write(new_text)
		os.system("sudo chmod +r %s" % nm)
		os.system("sudo chown root:root %s" % nm)
		os.system("sudo mv %s %s" % (nm, self.fname))
		os.system("sudo /usr/bin/newaliases")
		log.info("Alias file updated.")

