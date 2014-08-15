from leafecom.tests import *

class TestRentalsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='rentals', action='index'))
        # Test response...
