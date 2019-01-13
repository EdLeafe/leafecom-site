import json
import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class IpController(BaseController):

    def index(self, format=None):
        addr = str(request.remote_addr)
        if format is None:
            return addr
        elif format == "json":
            return json.dumps({"ip": addr})
        elif format == "xml":
            return "<ip>%s</ip>" % addr
