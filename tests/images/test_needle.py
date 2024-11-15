import unittest
import io
from src.images.needle import get_needle_into_buffer


class NeedleTest(unittest.TestCase):

    def setUp(self):
        return super().setUp()
    
    def tearDown(self):
        return super().tearDown()
    
    def test_needle_buffer(self):

        res = get_needle_into_buffer(2)
        assert isinstance(res, io.BytesIO)

