#!/usr/bin/env python
# -*- coding: utf-8 -*-

from leafecom.lib.base import BaseController, render

class DanController(BaseController):
	def index(self):
		return render("/dan.html")

