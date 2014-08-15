#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from pylons import request, response, session, tmpl_context as c
from leafecom.lib.base import BaseController, render

client_id = "1056749440127-iled6a38jk6n746479qmm6ud0ku02tml.apps.googleusercontent.com"
redirect_uri = "http://leafe.com:5000/oauth/callback/test"


class OauthController(BaseController):
	def index(self):
		return render("/oauthtest.html")

	def go(self, id=None):
		uri = "https://accounts.google.com/o/oauth2/auth?client_id=%s&response_type=code&redirect_uri=%s&scope=profile+https://www.googleapis.com/auth/plus.login"
		uri = uri % (client_id, redirect_uri)
		resp = requests.get(uri)
		return resp.content

	def callback(self, id=None):
		return request.params.get("code")
		return request.query_string
