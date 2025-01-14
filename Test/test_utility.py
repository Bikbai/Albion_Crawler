import time
from unittest import TestCase
import logging, json
from constants import Realm, EntityType, LOGGER_NAME
from utility import timer_decorator, setup_logger

log = setup_logger()

@timer_decorator(logger=log)
def sample_function():
    time.sleep(1)



class Test(TestCase):
    def test_timer(self):
        sample_function()
        self.assertTrue(True)

    def test_jsonarray(self):
        list_example = ["Mango", 1, 3, 6, "Oranges"];
        j = json.dumps(list_example)
        print(j)


