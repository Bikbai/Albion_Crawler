import time
from unittest import TestCase
import logging
from constants import Realm, EntityType, LOGGER_NAME
from utility import timer, setup_logger

log = setup_logger()

@timer(logger=log)
def sample_function():
    time.sleep(1)

class Test(TestCase):
    def test_timer(self):
        sample_function()
        self.assertTrue(True)


