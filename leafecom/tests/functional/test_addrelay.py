from leafecom.tests import *

class TestAddrelayController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='addrelay', action='index'))
        # Test response...
