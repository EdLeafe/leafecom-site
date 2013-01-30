# Add the virtual Python environment site-packages directory to the path
#import site
#site.addsitedir('/home/ed/pylons/leafe.com/env/lib/python2.5/site-packages')

# Avoid ``[Errno 13] Permission denied: '/var/www/.python-eggs'`` messages
import os
import newrelic.agent
os.environ['PYTHON_EGG_CACHE'] = '/home/ed/pylons/leafe.com/egg-cache'
newrelic.agent.initialize('/home/ed/pylons/leafe.com/newrelic.ini')

# Load the Pylons application
from paste.deploy import loadapp
#application = loadapp('config:/home/ed/pylons/leafe.com/production.ini')
# From the suggestion of Nathen Hinson, to fix the empty logging issue
from paste.script.util.logging_config import fileConfig
INIFILE = "/home/ed/pylons/leafe.com/production.ini"
fileConfig(INIFILE)
application = loadapp("config:%s" % INIFILE)
application = newrelic.agent.wsgi_application()(application)
