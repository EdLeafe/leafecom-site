from leafecom.tests import *

class TestUptimeController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='uptime', action='index'))
        # Test response...
