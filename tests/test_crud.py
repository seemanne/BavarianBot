import unittest
import logging
import sqlite3

import discord

from src.orm import init_db
import src.crud as crud
from src.client import Maggus
from .mocking import TaskConsumingLoop


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

    def test_tag_crud(self):
        tag_data_1 = {
            "name": "test_name_1",
            "description": "test description",
            "image_link": "http://testlink",
        }
        crud.add_tag(tag_data_1, self.client.sql_engine)

        tag = crud.get_tag("test_name_1 1", self.client.sql_engine)
        assert tag == "http://testlink"
        tag = crud.get_tag("non_existing_tag 2", self.client.sql_engine)
        assert tag.startswith("Failed to find")
        tag = crud.get_tag("non_existing_tag", self.client.sql_engine)
        assert tag.startswith("Sorry, I")

        tag_data_2 = {
            "name": "test_name_1",
            "description": "test description 2",
            "image_link": "http://testlink/different",
        }
        crud.add_tag(tag_data_2, self.client.sql_engine)

        embed = crud.list_tags("test_name_1", self.client.sql_engine)
        assert embed.description == "1 | test description\n2 | test description 2"

        tag_data_3 = {
            "name": "test_name_2",
            "description": "test description",
            "image_link": "http://testlink/different",
        }
        crud.add_tag(tag_data_3, self.client.sql_engine)
        embed = crud.list_all_tags(self.client.sql_engine)
        assert embed.description == "'test_name_1' : 2 tags\n'test_name_2' : 1 tags"

    def test_config_crud(self):
        crud.set_config("c_key", "c_val", self.client.sql_engine)

        assert crud.get_config("c_key", self.client.sql_engine) == "c_val"
        assert not crud.get_config("inex_key", self.client.sql_engine)

        crud.set_config("c_key", "c_val_1", self.client.sql_engine)

        crud.set_config("c_key_2", "c_val_2", self.client.sql_engine)
        assert crud.load_full_config(self.client.sql_engine) == {
            "c_key": "c_val_1",
            "c_key_2": "c_val_2",
        }

    def test_fish_crud(self):
        crud.save_fish("fisher", 69, 3, self.client.sql_engine)
        crud.save_fish("fisher_2", 69, 3, self.client.sql_engine)
        crud.save_fish("fisher", 42, 1, self.client.sql_engine)

        res = crud.get_all_catches_by_username("fisher", self.client.sql_engine)

        assert res["0"][0] == 42
        assert res["1"][0] == 69
        assert len(res.keys()) == 2
