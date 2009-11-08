from leafecom.tests import *

class TestDlsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='dls', action='index'))
        # Test response...
