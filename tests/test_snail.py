import unittest

from src.snail import check_for_twitter_link, snail_check
from src.datastructures import LRUCache
from .mocking import Message

class ClientTest(unittest.TestCase):

    def setUp(self) -> None:

        self.cache = LRUCache(5)

    def tearDown(self) -> None:
        pass

    def test_snail_negative(self):

        message = Message(
            content="https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUXbmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXA%3D"
        )
        is_link, cached = snail_check(message, self.cache)
        assert not is_link
        assert not cached

    def test_snail_not_snali(self):

        message = Message(
            content="https://twitter.com/tekbog/status/1738295383749488720"
        )
        is_link, cached = snail_check(message, self.cache)
        assert is_link
        assert not cached
    
    def test_snail_not_snali(self):

        message = Message(
            content="https://twitter.com/tekbog/status/1738295383749488720"
        )
        _, _ = snail_check(message, self.cache)
        is_link, cached = snail_check(message, self.cache)
        assert is_link
        assert cached