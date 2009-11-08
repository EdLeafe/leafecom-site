from leafecom.tests import *

class TestArchivesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='archives', action='index'))
        # Test response...
