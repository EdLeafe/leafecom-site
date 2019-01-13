# Avoid ``[Errno 13] Permission denied: '/var/www/.python-eggs'`` messages
import os
os.environ['PYTHON_EGG_CACHE'] = '/home/ed/projects/leafe.com/egg-cache'

# Load the Pylons application
from paste.deploy import loadapp
# From the suggestion of Nathen Hinson, to fix the empty logging issue
from paste.script.util.logging_config import fileConfig
INIFILE = "/home/ed/projects/leafe.com/production.ini"
fileConfig(INIFILE)
application = loadapp("config:%s" % INIFILE)
