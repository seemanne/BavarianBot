import unittest
import newspaper
from unittest.mock import patch
import logging

import discord

from src.client import Maggus

from src.cinephile import parse_movie, create_letterboxd_string, cinema_check
from .mocking import Message, TaskConsumingLoop, Channel


class FakeArticle:
    def __init__(self, url, **kwargs) -> None:
        self.url = url
        self.text = "This is parsed text from letterboxd"

    def download(self):
        pass

    def parse(self):
        pass


class FakeNoNumberArticle(FakeArticle):
    def __init__(self, url, **kwargs) -> None:
        super().__init__(url, **kwargs)

    def parse(self):
        if "1" in self.url or "2" in self.url:
            raise ValueError("Ayayay")


class ClientTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_parse_movie_basic(self):
        message_1 = Message(content="Can't wait to watch DUNE (2021) on IMAX")
        res = parse_movie(message_1)
        assert res[0] == "DUNE"
        assert res[1] == "2021"

    def test_no_movie(self):
        message_1 = Message(
            content="Can't wait to walk AROUND the BEACH (I am quite old)"
        )
        res = parse_movie(message_1)
        assert not res[0]
        assert not res[1]

    def test_parse_movie_spaced(self):
        message_1 = Message(content="Can't wait to watch POOR THINGS (2023)")
        res = parse_movie(message_1)
        assert res[0] == "POOR THINGS"
        assert res[1] == "2023"

    def test_parse_movie_colon(self):
        message_1 = Message(content="Can't wait to watch DUNE: PART TWO (2023)")
        res = parse_movie(message_1)
        assert res[0] == "DUNE PART TWO"
        assert res[1] == "2023"

    def test_parse_movie_apo(self):
        message_1 = Message(content="Can't wait to watch THE TEACHERS' LOUNGE (2024)")
        res = parse_movie(message_1)
        assert res[0] == "THE TEACHERS LOUNGE"
        assert res[1] == "2024"

    def test_parse_movie_numbers(self):
        message_1 = Message(
            content="Can't wait to watch 10 THINGS I HATE ABOUT YOU (1999)"
        )
        res = parse_movie(message_1)
        assert res[0] == "10 THINGS I HATE ABOUT YOU"
        assert res[1] == "1999"

    def test_create_letterboxd_string(self):
        res = create_letterboxd_string("DUNE PART TWO ", "2024")
        assert (
            res[0]
            == "https://letterboxd.com/film/dune-part-two-2024/reviews/by/activity/"
        )
        assert (
            res[1] == "https://letterboxd.com/film/dune-part-two/reviews/by/activity/"
        )

    def test_cinema_check_negative(self):
        logger = logging.getLogger()
        client = Maggus(
            intents=discord.Intents.all(),
            log=logger,
            in_test=True,
            test_loop=TaskConsumingLoop(),
        )
        message_1 = Message(
            content="Can't wait to walk AROUND the BEACH (I am quite old)"
        )
        cinema_check(message_1, client.loop)

    @patch("newspaper.Article", new=FakeArticle)
    def test_cinema_check_with_year(self):
        logger = logging.getLogger()
        client = Maggus(
            intents=discord.Intents.all(),
            log=logger,
            in_test=True,
            test_loop=TaskConsumingLoop(),
        )
        message_1 = Message(content="Can't wait to DUNE (2021) on IMAX")
        client.cinephile(message_1)
        client.loop.run_tasks()

        assert message_1.channel.test_message_sent.embed.title == "DUNE 2021"
        assert (
            message_1.channel.test_message_sent.embed.url
            == "https://letterboxd.com/film/dune-2021"
        )
        assert (
            message_1.channel.test_message_sent.embed.description
            == "This is parsed text from letterboxd"
        )

    @patch("newspaper.Article", new=FakeNoNumberArticle)
    def test_cinema_check_without_year(self):
        logger = logging.getLogger()
        client = Maggus(
            intents=discord.Intents.all(),
            log=logger,
            in_test=True,
            test_loop=TaskConsumingLoop(),
        )
        message_1 = Message(content="Can't wait to DUNE (2021) on IMAX")
        client.cinephile(message_1)
        client.loop.run_tasks()

        assert message_1.channel.test_message_sent.embed.title == "DUNE"
        assert (
            message_1.channel.test_message_sent.embed.url
            == "https://letterboxd.com/film/dune"
        )
        assert (
            message_1.channel.test_message_sent.embed.description
            == "This is parsed text from letterboxd"
        )
