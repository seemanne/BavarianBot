import datetime
import unittest
from unittest.mock import patch
import sqlalchemy

from src.orm import init_db
from src.snail import SnailState, LinkChecker, PollingStation, CachedXeet
from .mocking import Message, Author, TaskConsumingLoop


def fake_random(res):

    def func():
        return res
    return func

async def fake_sleep(time):

    return


class SnailTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sql_engine = sqlalchemy.create_engine("sqlite:///:memory:")
        init_db(self.sql_engine)
        self.snail_state = SnailState(5, self.sql_engine)
        self.loop = TaskConsumingLoop()

    def tearDown(self) -> None:
        pass

    @patch("random.random", new=fake_random(0.1))
    @patch("asyncio.sleep", new=fake_sleep)
    def test_snail_negative(self):
        message = Message(
            content="https://news.ycombinator.com/item?id=42134964",
            author=Author(),
            jump_url="message_jump_url",
            reference=None
        )
        self.loop.create_task(self.snail_state.check_snail(message))
        self.loop.run_tasks()
        assert len(self.snail_state.snail_cache) == 0

    @patch("random.random", new=fake_random(0.1))
    @patch("asyncio.sleep", new=fake_sleep)
    def test_snail_not_snail(self):
        message = Message(
            content="https://twitter.com/tekbog/status/1738295383749488720",
            author=Author(),
            jump_url="message_jump_url",
            reference=None
        )
        self.loop.create_task(self.snail_state.check_snail(message))
        self.loop.run_tasks()
        assert len(self.snail_state.snail_cache) == 1

    @patch("random.random", new=fake_random(0.1))
    @patch("asyncio.sleep", new=fake_sleep)
    @patch("src.snail.PollingStation.update_needle", new=fake_sleep)
    def test_snail_is_snail(self):
        message = Message(
            content="https://twitter.com/tekbog/status/1738295383749488720",
            author=Author(),
            jump_url="message_jump_url",
            reference=None
        )
        self.loop.create_task(self.snail_state.check_snail(message))
        self.loop.create_task(self.snail_state.check_snail(message))
        self.loop.run_tasks()
        assert len(self.snail_state.snail_cache) == 1
        assert self.snail_state.snail_cache.get("1738295383749488720").post_count == 2

    @patch("asyncio.create_task", new=fake_sleep)
    def test_ballot_stuffing(self):
        
        polling_station = PollingStation()
        voter = "<@123456789>"
        polling_station.vote_yes(voter)
        assert not polling_station.vote_no(voter)

    @patch("asyncio.create_task", new=fake_sleep)
    def test_ballot_counting(self):
        
        polling_station = PollingStation()
        voter_1 = "<@1234567891>"
        voter_2 = "<@1234567892>"
        voter_3 = "<@1234567893>"
        polling_station.vote_yes(voter_1)
        polling_station.vote_no(voter_2)
        polling_station.vote_no(voter_3)

        res = polling_station.count_ballots(False, self.sql_engine)
        assert "was not snail!" in res
        assert voter_1 in res
        assert voter_2 in res
        assert voter_3 in res
    

    def test_dump_and_load(self):

        xeet_1 = CachedXeet(
            tweet_id="1234",
            initial_poster_name="poster_1",
            initial_jump_url="jump_url_1",
        )
        xeet_2 = CachedXeet(
            tweet_id="5678",
            initial_poster_name="poster_2",
            initial_jump_url="jump_url_2",
        )
        xeet_2.initial_post_time=datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
        

        self.snail_state.snail_cache.put(xeet_1.tweet_id, xeet_1)
        self.snail_state.snail_cache.put(xeet_2.tweet_id, xeet_2)
        self.snail_state.dump_to_db()
        new_state = SnailState(5, self.sql_engine)
        new_state.load_from_db()

        assert len(new_state.snail_cache) == 2
        assert list(new_state.snail_cache.cache.values())[0] == list(self.snail_state.snail_cache.cache.values())[0]

        new_state.dump_to_db()
    
    def test_empty_load(self):

        self.snail_state.load_from_db()
    
class LinkCheckerTest(unittest.TestCase):

    def setUp(self):
        
        self.checker = LinkChecker()
    
    def test_twitter_links(self):

        assert self.checker.check_message("https://twitter.com/tekbog/status/1738295383749488720")[0]
        assert self.checker.check_message("this is a post: https://twitter.com/tekbog/status/1738295383749488720")[0]
        assert self.checker.check_message("https://fxtwitter.com/tekbog/status/1738295383749488720")[0]
        assert self.checker.check_message("https://x.com/tekbog/status/1738295383749488720")[0]
        assert self.checker.check_message("https://twitter.com/tekbog/status/1738295383749488720?t=bqEHRy2klOJBiQ-2XnnemA&s=19")[0]