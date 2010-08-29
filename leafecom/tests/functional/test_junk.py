from leafecom.tests import *

class TestJunkController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='junk', action='index'))
        # Test response...
