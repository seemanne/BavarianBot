import unittest
import logging
import sqlite3

import discord

from src.orm import init_db
from src.client import Maggus
from .mocking import Message, TaskConsumingLoop

class ClientTest(unittest.TestCase):

    def setUp(self) -> None:

        self.logger = logging.getLogger()
        self.client = Maggus(intents=discord.Intents.all(), log=self.logger, in_test=True, test_loop=TaskConsumingLoop())
        init_db(self.client.sql_engine)
    
    def tearDown(self) -> None:
        
        conn = sqlite3.connect("sqlite:///../db/test.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            self.logger.info(f"Table '{table_name}' dropped.")

        conn.commit()
        conn.close()
