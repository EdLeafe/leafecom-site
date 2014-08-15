#!/usr/bin/env python
# -*- coding: utf-8 -*-

from leafecom.lib.base import BaseController, render


class OregonController(BaseController):
	def index(self):
		return render("/oregon.html")

	def test(self):
		return render("/oauthtest.html")
