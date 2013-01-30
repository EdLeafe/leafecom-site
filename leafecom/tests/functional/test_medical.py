from leafecom.tests import *

class TestMedicalController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='medical', action='index'))
        # Test response...
