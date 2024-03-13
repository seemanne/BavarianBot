import unittest
import logging
import sqlite3
from unittest.mock import patch

import discord

from src.orm import init_db
from src.client import Maggus
from .mocking import Message, TaskConsumingLoop


class ClientTest(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger()
        self.client = Maggus(
            intents=discord.Intents.all(),
            log=self.logger,
            in_test=True,
            test_loop=TaskConsumingLoop(),
        )
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

    def test_tagger_empty(self):
        message = Message(content="$tag")
        self.client.tagger(message)

        self.client.loop.run_tasks()

        assert (
            message.test_reply.reply
            == "Sorry, but that tag was not recognized. Try listing tags with $tag list or using $tag help"
        )

    def test_tagger_add(self):
        message_1 = Message(content="$tag add")
        self.client.tagger(message_1)
        assert self.client.message_hooks

        message_2 = Message(content="http://test-image")
        self.client.process_message_hooks(message_2)
        message_3 = Message(content="test_tag")
        self.client.process_message_hooks(message_3)
        message_4 = Message(content="test_tag description, high detail")
        self.client.process_message_hooks(message_4)

        self.client.loop.run_tasks()

        assert message_1.test_reply.reply
        assert message_2.test_reply.reply
        assert message_3.test_reply.reply
        assert message_4.test_reply.reply == "Tag creation successful"

    def test_tagger_add_failures(self):
        message_1 = Message(content="$tag add")
        self.client.tagger(message_1)
        message_2 = Message(content="http://test-image")
        self.client.process_message_hooks(message_2)
        message_3 = Message(content="help")
        self.client.process_message_hooks(message_3)
        message_4 = Message(content="test_tag")
        self.client.process_message_hooks(message_4)
        message_5 = Message(content="test_tag description, high detail")
        self.client.process_message_hooks(message_5)

        self.client.loop.run_tasks()

        assert message_1.test_reply.reply
        assert message_3.test_reply.reply.__contains__("Banned tag name")
        assert message_5.test_reply.reply == "Tag creation successful"

    @patch("src.crud.get_tag", new=lambda x, y: "test_tag")
    def test_post_tag(self):
        message = Message(content="$tag gandalf 1")
        self.client.post_tag(message)

        self.client.loop.run_tasks()
        assert message.test_reply.reply == "test_tag"

    @patch(
        "src.crud.list_all_tags",
        new=lambda x: discord.Embed(
            title="Available tags", description="Embed desc all"
        ),
    )
    @patch(
        "src.crud.list_tags",
        new=lambda x, y: discord.Embed(
            title="Available tags", description="Embed desc single"
        ),
    )
    def test_list_tags(self):
        message_1 = Message(content="$tag list")
        self.client.list_tags(message_1)
        message_2 = Message(content="$tag list gandalf")
        self.client.list_tags(message_2)

        self.client.loop.run_tasks()

        assert message_1.test_reply.embed.description == "Embed desc all"
        assert message_2.test_reply.embed.description == "Embed desc single"
