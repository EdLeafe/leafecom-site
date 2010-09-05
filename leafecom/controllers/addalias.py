import logging
import os
from subprocess import Popen, PIPE
import tempfile

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

def runproc(cmd):
	return Popen([cmd], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)


class AddaliasController(BaseController):
	def index(self, id=None):
		self.fname = "/etc/aliases"
		self.sep = "### USERS ###"
		fulltxt = file(self.fname).read()
		self.aliasPattern = "ed-%s: ed"
		self.sections = fulltxt.split(self.sep)

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

	
	def _addAlias(self, nm):
		mailnames = self.sections[1].strip().splitlines()
		newalias = self.aliasPattern % nm
		log.debug("XXXXXX NewAlias: %s" % newalias)
		mailnames.append(newalias)
		mailnames.sort()
		self._writeNewAliasFile(mailnames)
		return "<h2>Alias %s added</h2>" % nm

	
	def _delAlias(self, nm):
		mailnames = self.sections[1].strip().splitlines()
		delalias = self.aliasPattern % nm
		log.debug("XXXXXX DelAlias: %s" % delalias)
		try:
			mailnames.remove(delalias)
		except ValueError:
			return "No such alias: %s" % delalias
		mailnames.sort()
		self._writeNewAliasFile(mailnames)
		return "<h2>Alias %s deleted</h2>" % nm


	def _writeNewAliasFile(self, mailnames):
		updated_names = "\n".join(set(mailnames))
		updated_txt = "\n".join([self.sections[0].strip(), self.sep,
				updated_names, self.sep, self.sections[2].lstrip()])
		fd, nm  = tempfile.mkstemp()
		os.close(fd)
		file(nm, "w").write(updated_txt)
		os.system("sudo mv %s %s" % (nm, self.fname))
		os.system("sudo newaliases")

