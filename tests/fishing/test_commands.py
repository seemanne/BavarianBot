import asyncio
import unittest
from unittest.mock import patch
from ..mocking import MagicObject, Interaction, Author, gather_all_coroutines
from src.fishing.commands import start_fishing, reel_fish
from src.fishing.pond import Pond


def fake_randint(*args):
    return 0.2


def dummy(*args, **kwargs):
    pass


@patch("random.randint", new=fake_randint)
@patch("src.fishing.commands.FISHING_REACTION_SECONDS", new=0.2)
@patch("src.crud.save_fish", new=dummy)
class ClientTest(unittest.TestCase):
    def setUp(self) -> None:
        pond = Pond()
        pond._populate()
        self.client = MagicObject(
            is_dev=False,
            pond=pond,
            sql_engine=None,
        )
        self.user = Author()

    def tearDown(self) -> None:
        pass

    def test_start_fishing_no_reel(self):
        interation_1 = Interaction(
            client=self.client,
            user=self.user,
        )
        asyncio.run(start_fishing.callback(interation_1))

        assert "has started" in interation_1.response.test_message_sent
        assert (
            "fish is biting" in interation_1.channel.all_test_messages_sent[0].content
        )
        assert (
            "failed to catch" in interation_1.channel.all_test_messages_sent[1].content
        )

        interation_2 = Interaction(
            client=self.client,
            user=self.user,
        )
        asyncio.run(start_fishing.callback(interation_2))
        assert "has started" in interation_2.response.test_message_sent

    def test_start_fishing_already_fishing(self):
        interation_1 = Interaction(
            client=self.client,
            user=self.user,
        )
        interation_2 = Interaction(
            client=self.client,
            user=self.user,
        )
        asyncio.run(
            gather_all_coroutines(
                [
                    start_fishing.callback(interation_1),
                    start_fishing.callback(interation_2),
                ]
            )
        )
        assert "already using your rod" in interation_2.response.test_message_sent

    def test_early_reel(self):
        interaction_1 = Interaction(client=self.client, user=self.user)
        interaction_2 = Interaction(client=self.client, user=self.user)

        asyncio.run(
            gather_all_coroutines(
                [
                    start_fishing.callback(interaction_1),
                    reel_fish.callback(interaction_2),
                ]
            )
        )
        assert (
            "already tried to /reel"
            in interaction_1.channel.latest_test_message_sent.content
        )

    def test_successful_reel(self):
        interaction_1 = Interaction(client=self.client, user=self.user)
        interaction_2 = Interaction(client=self.client, user=self.user)

        async def chill_and_reel():
            await asyncio.sleep(0.1)
            await reel_fish.callback(interaction_2)

        asyncio.run(
            gather_all_coroutines(
                [start_fishing.callback(interaction_1), chill_and_reel()]
            )
        )
        assert "you are holding the fish" in interaction_2.response.test_message_sent
        assert len(interaction_1.channel.all_test_messages_sent) == 1

    def test_reel_too_late(self):
        interaction_1 = Interaction(client=self.client, user=self.user)
        interaction_2 = Interaction(client=self.client, user=self.user)

        async def chill_and_reel():
            await asyncio.sleep(0.5)
            await reel_fish.callback(interaction_2)

        asyncio.run(
            gather_all_coroutines(
                [start_fishing.callback(interaction_1), chill_and_reel()]
            )
        )
        assert "you missed the fish" in interaction_2.response.test_message_sent
        assert len(interaction_1.channel.all_test_messages_sent) == 2

    def test_reel_no_fish(self):
        interaction_1 = Interaction(client=self.client, user=self.user)
        asyncio.run(reel_fish.callback(interaction_1))
        assert "you're not fishing" in interaction_1.response.test_message_sent
