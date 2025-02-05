from unittest import TestCase
from event_batch_processor import convert_timestamp

class Test(TestCase):
    def test_convert_timestamp(self):
        x = convert_timestamp("2025-01-26T17:24:11.730405200Z")
        print(x)
        self.fail()
