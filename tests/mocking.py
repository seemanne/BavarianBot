import asyncio


class MagicObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Message:
    def __init__(self, id=11111, channel=None, author=None, **kwargs):
        self.id = id
        if not channel:
            channel = Channel()
        self.channel = channel
        if not author:
            author = Author()
        self.author = author
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def reply(self, reply=None, **kwargs):
        self.test_reply = MagicObject(reply=reply, **kwargs)

    async def add_reaction(self, object=None, **kwargs):
        self.test_reactions_added = MagicObject(object=object, **kwargs)


class Channel:
    def __init__(self, id=22222, type="public", **kwargs) -> None:
        self.id = id
        self.type = type
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def send(self, **kwargs):
        self.test_message_sent = MagicObject(**kwargs)


class Author:
    def __init__(self, id=33333, name="test_author", **kwargs) -> None:
        self.id = id
        self.name = name
        self.mention = f"<{id}|{name}>"
        for key, value in kwargs.items():
            setattr(self, key, value)


class TaskConsumingLoop:
    def __init__(self) -> None:
        self.coro_list = []

    def create_task(self, coro):
        self.coro_list.append(coro)

    def run_tasks(self):
        async def gathering():
            await asyncio.gather(*self.coro_list)
            self.coro_list = []

        asyncio.run(gathering())
