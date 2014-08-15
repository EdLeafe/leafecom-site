from leafecom.tests import *

class TestBitcoinczController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='bitcoincz', action='index'))
        # Test response...
