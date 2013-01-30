from leafecom.tests import *

class TestPyexifController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='pyexif', action='index'))
        # Test response...
