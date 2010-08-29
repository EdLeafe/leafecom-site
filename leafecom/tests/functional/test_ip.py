from leafecom.tests import *

class TestIpController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='ip', action='index'))
        # Test response...
