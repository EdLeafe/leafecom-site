from leafecom.tests import *

class TestVaultController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='vault', action='index'))
        # Test response...
