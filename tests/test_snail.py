import unittest
from unittest.mock import patch

from src.snail import SnailState, check_for_twitter_link
from src.datastructures import LRUCache
from .mocking import Message, Author, TaskConsumingLoop


def fake_random(res):

    def func():
        return res
    return func


class ClientTest(unittest.TestCase):
    def setUp(self) -> None:
        self.snail_state = SnailState(5)
        self.loop = TaskConsumingLoop()

    def tearDown(self) -> None:
        pass

    @patch("random.random", new=fake_random(0.1))
    def test_snail_negative(self):
        message = Message(
            content="https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUXbmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXA%3D",
            author=Author(),
            jump_url="message_jump_url"
        )
        self.loop.create_task(self.snail_state.check_snail(message))
        assert len(self.snail_state.snail_cache) == 0

    @patch("random.random", new=fake_random(0.1))
    def test_snail_not_snail(self):
        message = Message(
            content="https://twitter.com/tekbog/status/1738295383749488720",
            author=Author(),
            jump_url="message_jump_url"
        )
        self.loop.create_task(self.snail_state.check_snail(message))
        self.loop.run_tasks()
        assert len(self.snail_state.snail_cache) == 1

    @patch("random.random", new=fake_random(0.1))
    def test_snail_is_snail(self):
        message = Message(
            content="https://twitter.com/tekbog/status/1738295383749488720",
            author=Author(),
            jump_url="message_jump_url"
        )
        self.loop.create_task(self.snail_state.check_snail(message))
        self.loop.create_task(self.snail_state.check_snail(message))
        self.loop.run_tasks()
        assert len(self.snail_state.snail_cache) == 1
        assert self.snail_state.snail_cache.get("1738295383749488720").post_count == 2
