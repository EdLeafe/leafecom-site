from leafecom.tests import *

class TestProfoxFaqController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='profox_faq', action='index'))
        # Test response...
