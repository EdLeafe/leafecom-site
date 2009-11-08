from leafecom.tests import *

class TestConsultingController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='consulting', action='index'))
        # Test response...
