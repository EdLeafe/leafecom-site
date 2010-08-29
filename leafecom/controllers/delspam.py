import os
import logging
import random

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)
colors = ['indigo', 'gold', 'hotpink', 'firebrick', 'indianred', 'yellow', 'mistyrose', 
		'darkolivegreen', 'olive', 'darkseagreen', 'pink', 'tomato', 'feldspar', 
		'lightcoral', 'orangered', 'navajowhite', 'teal', 'lime', 'palegreen', 
		'darkslategrey', 'greenyellow', 'burlywood', 'seashell', 'mediumspringgreen', 
		'fuchsia', 'papayawhip', 'blanchedalmond', 'chartreuse', 'dimgray', 'black', 
		'peachpuff', 'springgreen', 'aquamarine', 'white', 'orange', 'lightsalmon', 
		'darkslategray', 'violetred', 'brown', 'ivory', 'dodgerblue', 'peru', 'lawngreen', 
		'chocolate', 'crimson', 'forestgreen', 'darkgrey', 'lightseagreen', 'cyan', 
		'mintcream', 'silver', 'antiquewhite', 'mediumorchid', 'skyblue', 'gray', 
		'darkturquoise', 'goldenrod', 'darkgreen', 'floralwhite', 'darkviolet', 'darkgray', 
		'moccasin', 'saddlebrown', 'grey', 'darkslateblue', 'lightskyblue', 'lightpink', 
		'mediumvioletred', 'slategrey', 'red', 'deeppink', 'limegreen', 'darkmagenta', 
		'palegoldenrod', 'plum', 'turquoise', 'lightgrey', 'lightgoldenrodyellow', 
		'darkgoldenrod', 'lavender', 'maroon', 'yellowgreen', 'sandybrown', 'thistle', 
		'violet', 'navy', 'magenta', 'dimgrey', 'tan', 'rosybrown', 'olivedrab', 'blue', 
		'lightblue', 'ghostwhite', 'honeydew', 'cornflowerblue', 'slateblue', 'linen', 
		'darkblue', 'powderblue', 'seagreen', 'darkkhaki', 'snow', 'sienna', 'mediumblue', 
		'royalblue', 'lightcyan', 'green', 'mediumpurple', 'midnightblue', 'cornsilk', 
		'paleturquoise', 'bisque', 'slategray', 'darkcyan', 'khaki', 'wheat', 
		'lightslateblue', 'darkorchid', 'deepskyblue', 'salmon', 'darkred', 'steelblue', 
		'palevioletred', 'lightslategray', 'aliceblue', 'lightslategrey', 'lightgreen', 
		'orchid', 'gainsboro', 'mediumseagreen', 'lightgray', 'mediumturquoise', 
		'lemonchiffon', 'cadetblue', 'lightyellow', 'lavenderblush', 'coral', 'purple', 
		'aqua', 'whitesmoke', 'mediumslateblue', 'darkorange', 'mediumaquamarine', 
		'darksalmon', 'beige', 'blueviolet', 'azure', 'lightsteelblue', 'oldlace']


class DelspamController(BaseController):

	def index(self, id):
		tmplt = """
<html>
<body bgcolor="%s">
%s
</body>
</html>"""
		fname = os.path.join("/home/ed/spam/checked", id)
		if id.startswith("spam"):
			bg = "tan"
		else:
			bg = "lightsteelblue"
		try:
			os.unlink(fname)
			#msg = ("<h2 style='color: %s'>File %s has been deleted.</h2>" % (random.choice(colors), id) for i in xrange(99))
			msg = "<h1 style='color: black'>File %s has been deleted.</h1>" % id
		except OSError, e:
			#msg = ("<h2 style='color: %s'>Couldn't delete %s: %s</h2>" % (random.choice(colors), id, e) for i in xrange(99))
			msg = "<h1 style='color: red'>Couldn't delete %s: %s</h1>" % (id, e[1])
		#return tmplt % (bg, "\n".join(msg))
		return tmplt % (bg, msg)

