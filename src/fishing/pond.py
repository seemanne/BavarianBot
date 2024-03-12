import random
import datetime
import asyncio
from src.datastructures import RandomStack


POND_SIZE = 10

BIG_FAN_LIST = [
    "Taylor Swift",
    "Sopher",
    "your Mom",
    "Alex",
    "feet",
    "that time of the year when the sun sets just right at bedtime",
    "christmas music",
    "posting tweets in #general. Good riddance",
    "watching gammbus fish",
    "going to bed early",
    "Fishmas",
]

WORKPLACE_LIST = [
    "a dog viagra startup",
    "washington-based policy think tank",
    "X, but got fired a year ago and hasn't been employed since",
    "X",
    "Hooters",
    "a daycare",
    "Santas elf factory",
    "home, totally isolated from its swarm",
]

WISHES_LIST = [
    "you celebrate fishmas with your whole family. How wholesome!",
    "you would shower more often",
    "more people were informed about the envoironmental impact of fishing",
    "you were more productive at work",
    "printers were less smeary",
    "a nice high paid hedgefund job",
]


class Fish:
    def __init__(self) -> None:
        self.weight = random.randrange(80, 4200, 35) + random.randint(0, 9)
        self.n_times_fed = 0
        self.children = random.randint(0, 5)
        self.wives = random.randint(0, 3)
        self.big_fan = random.choice(BIG_FAN_LIST)
        self.workplace = random.choice(WORKPLACE_LIST)
        self.wish = random.choice(WISHES_LIST)

        self.funfact_functions = [
            self.funfact_fan,
            self.funfact_workplace,
            self.funfact_wives,
            self.funfact_wishes,
        ]

    def feed(self):
        additional_weight = random.randint(500, 1000)
        self.n_times_fed += 1
        self.weight += additional_weight

        return additional_weight

    def get_catch_message(self, fisher_name):
        message = (
            f"Congratulations {fisher_name}, you are holding the fish in your hand!"
        )

        message += f" Your fish weighs {self.weight}g"
        if self.n_times_fed:
            message += f" and has been fed by others {self.n_times_fed} time(s)"
        message += "."
        message += self.get_funfact()

        return message

    def get_funfact(self):
        funfact = random.choice(self.funfact_functions)
        return funfact()

    def funfact_fan(self):
        return f" It was a big fan of {self.big_fan}!"

    def funfact_workplace(self):
        return f" It worked at {self.workplace}."

    def funfact_wives(self):
        if self.wives > 1:
            return f" His {self.wives} wives will miss him dearly!"
        if self.wives:
            return " His wife will have to take care of his estate."
        return " He remained single forever."

    def funfact_wishes(self):
        rand = random.random()
        if rand < 0.5:
            return f" She secretly wished that {self.wish}"
        else:
            return f" He secretly wished that {self.wish}"


class Pond:
    def __init__(self) -> None:
        self.fishes = RandomStack()
        self.fishers = {}
        self.ecosystem_task = None

    def refill_fish(self):
        if (
            len(self.fishes) < POND_SIZE
            and datetime.datetime.now().hour < 23
            and datetime.datetime.now().hour > 6
        ):
            self.fishes.put(Fish())

    def populate_pond_and_start_ecosystem(self): # pragma: no cover
        self._populate()
        self.ecosystem_task = asyncio.get_event_loop().create_task(
            self._ecosystem_loop()
        )

    def get_fisher(self, name: str):
        return (name in self.fishers, self.fishers.get(name, None))

    def pop_fisher(self, name: str):
        return (name in self.fishers, self.fishers.pop(name, None))

    def add_fisher(self, name: str, time: datetime.datetime):
        self.fishers[name] = time

    def get_fish(self) -> Fish:
        return self.fishes.get()

    def return_fish(self, fish: Fish):
        self.fishes.put(fish)

    async def _ecosystem_loop(self): # pragma: no cover
        await asyncio.sleep(5)

        while True:
            if (
                len(self.fishes) < POND_SIZE
                and datetime.datetime.now().hour < 23
                and datetime.datetime.now().hour > 6
            ):
                self.fishes.put(Fish())

            await asyncio.sleep(random.randint(30, 90))

    def _populate(self):
        for _ in range(POND_SIZE):
            self.fishes.put(Fish())