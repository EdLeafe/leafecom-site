from leafecom.tests import *

class TestDelspamController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='delspam', action='index'))
        # Test response...
