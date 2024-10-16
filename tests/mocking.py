import asyncio


async def gather_all_coroutines(coroutines):
    await asyncio.gather(*coroutines)


class MagicObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Message:
    def __init__(self, id=11111, channel=None, author=None, **kwargs):
        self.id = id
        self.edits = []
        if not channel:
            channel = Channel()
        self.channel = channel
        if not author:
            author = Author()
        self.author = author
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    async def edit(self, **kwargs):
        self.edits.append(kwargs)

    async def reply(self, reply=None, **kwargs):
        self.test_reply = MagicObject(reply=reply, **kwargs)
        return Message()
    
    async def delete(self, **kwargs):
        self.is_deleted = True

    async def add_reaction(self, object=None, **kwargs):
        self.test_reactions_added = MagicObject(object=object, **kwargs)


class Channel:
    def __init__(self, id=22222, type="public", **kwargs) -> None:
        self.id = id
        self.type = type
        self.all_test_messages_sent = []
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def send(self, content=None, **kwargs):
        self.all_test_messages_sent.append(MagicObject(content=content, **kwargs))
        self.latest_test_message_sent = MagicObject(content=content, **kwargs)


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


class Interaction:
    def __init__(self, id=44444, channel=None, author=None, **kwargs) -> None:
        self.id = id
        if not channel:
            channel = Channel()
        self.channel = channel
        if not author:
            author = Author()
        self.response = InteractionResponse()
        for key, value in kwargs.items():
            setattr(self, key, value)


class InteractionResponse:
    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def send_message(self, content):
        self.test_message_sent = content
