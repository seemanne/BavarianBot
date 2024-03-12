import unittest
import random
from unittest.mock import patch

from src.fishing.pond import Pond, Fish


class Hour:
    def __init__(self, hour) -> None:
        self.hour = hour


class FakeEuroTime:
    def now(self):
        return Hour(12)


class FakeNATime:
    def now(self):
        return Hour(1)


class ClientTest(unittest.TestCase):
    def setUp(self) -> None:
        random.seed = 42

    def tearDown(self) -> None:
        pass

    def test_fish(self):
        fish = Fish()

        message = fish.get_catch_message("fisher")
        assert "has been fed by others" not in message

        fish.feed()
        message = fish.get_catch_message("fisher")
        assert "has been fed by others" in message

        for i in range(20):
            # hack to call all possible messages
            fish.get_catch_message("fisher")

        fish.wives = 0
        fish.funfact_wives()
        fish.wives = 1
        fish.funfact_wives()
        fish.wives = 2
        fish.funfact_wives()

    @patch("datetime.datetime", new=FakeEuroTime())
    def test_euro_hours(self):
        pond = Pond()
        pond.refill_fish()
        assert len(pond.fishes) > 0

    @patch("datetime.datetime", new=FakeNATime())
    def test_na_hours(self):
        pond = Pond()
        pond.refill_fish()
        assert len(pond.fishes) == 0

    def test_pond_fishes(self):
        pond = Pond()
        pond._populate()
        n_fish = len(pond.fishes)

        fish = pond.get_fish()
        assert len(pond.fishes) < n_fish
        pond.return_fish(fish)
        assert len(pond.fishes) == n_fish

    def test_pond_fishers(self):
        pond = Pond()
        pond.add_fisher("fisher", True)

        is_there, time = pond.get_fisher("fisher")
        assert is_there
        assert time

        is_there, time = pond.pop_fisher("fisher")
        assert is_there
        assert time

        is_there, time = pond.get_fisher("fisher")
        assert not is_there
        assert not time

        is_there, time = pond.pop_fisher("fisher")
        assert not is_there
        assert not time
