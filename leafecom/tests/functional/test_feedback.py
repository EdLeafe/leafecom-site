from leafecom.tests import *

class TestFeedbackController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='feedback', action='index'))
        # Test response...
