from leafecom.tests import *

class TestAddaliasController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='addalias', action='index'))
        # Test response...
