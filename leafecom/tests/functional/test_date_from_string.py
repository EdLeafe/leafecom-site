from leafecom.tests import *

class TestDateFromStringController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='date_from_string', action='index'))
        # Test response...
