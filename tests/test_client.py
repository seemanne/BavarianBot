import unittest
import logging
import sqlite3

import discord

from src.orm import init_db
from src.client import Maggus
from .mocking import Message, TaskConsumingLoop, Channel

class ClientTest(unittest.TestCase):

    def setUp(self) -> None:

        self.logger = logging.getLogger()
        self.client = Maggus(intents=discord.Intents.all(), log=self.logger, in_test=True, test_loop=TaskConsumingLoop())
        init_db(self.client.sql_engine)
    
    def tearDown(self) -> None:
        
        conn = sqlite3.connect("sqlite:///../test.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            self.logger.info(f"Table '{table_name}' dropped.")

        conn.commit()
        conn.close()

    def test_countdown_check(self):

        right_channel = Channel(id=874290704522821694)
        wrong_channel = Channel()

        message_1 = Message(
            content="<@660689481984376843> 69420",
            channel=right_channel
        )
        message_2 = Message(
            content="<@660689481984376843> 69419",
            channel=right_channel
        )
        message_3 = Message(
            content="<@660689481984376843> 69420",
            channel=right_channel
        )
        message_4 = Message(
            content="<@660689481984376843> 69418",
            channel=wrong_channel
        )

        self.client.countdown_check(message_1)
        assert self.client.countdown_cache

        self.client.countdown_check(message_2)
        self.client.countdown_check(message_3)
        self.client.countdown_check(message_4)

        self.client.loop.run_tasks()

        assert message_3.test_reactions_added.object == "🤥"
        assert self.client.countdown_cache == 69419