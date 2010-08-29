from leafecom.tests import *

class TestLisafController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='lisaf', action='index'))
        # Test response...
