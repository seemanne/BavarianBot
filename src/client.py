import asyncio
import datetime
import logging
import re
from typing import Any
import sqlalchemy
import discord
from discord import app_commands

import src.cinephile
import src.tagger
import src.auth
import src.orm
import src.crud
import src.models
import src.command_tree
import src.snail
import src.datastructures
import src.fishing.pond


class Maggus(discord.Client):
    def __init__(
        self,
        *,
        intents: discord.Intents,
        log: logging.Logger,
        in_test: bool = False,
        test_loop=None,
        **options,
    ):
        if in_test:
            self.loop = test_loop
            self.in_test = True
        else:
            self.in_test = False
            super().__init__(intents=intents, **options)
            self.tree = app_commands.CommandTree(self)
        self.log = log
        self.is_dev = src.auth.DEV

        if in_test:
            db_url = "sqlite:///:memory:"
            ro_url = "sqlite:///:memory:?mode=ro&uri=true"
        else:
            db_url = "sqlite:///db/chalkotheke.db"
            ro_url = "sqlite:///file:db/chalkotheke.db?mode=ro&uri=true"
        self.sql_engine = sqlalchemy.create_engine(db_url)
        self.sql_engine_ro = sqlalchemy.create_engine(ro_url)

        self.activated = True
        self.snail_lock = False

        self.message_hooks: dict[int, src.tagger.TagCreationFlow] = {}

        self.pond = src.fishing.pond.Pond()
        self.snail_state = src.snail.SnailState(10000, self.sql_engine)
        self.countdown_cache = None
        self.most_recent_message_id = None

    def __repr__(self) -> str:
        return "BavarianClient"

    def __str__(self) -> str:
        return "BavarianClient"

    async def setup_hook(self):
        if self.is_dev:
            guild_id = 143381234494603264
            self.log.setLevel(logging.DEBUG)
        else:
            guild_id = 389103804835954699

        for command in src.command_tree.LIST_OF_COMMANDS:
            self.tree.add_command(command)

        self.tree.on_error = src.command_tree.on_error

        self.tree.copy_global_to(guild=discord.Object(id=guild_id))
        await self.tree.sync(guild=discord.Object(id=guild_id))
        self.log.info("Synced command tree")

        self.pond.populate_pond_and_start_ecosystem()
        self.log.info("Started pond ecosystem")

        self.feedback_webhook = discord.Webhook.from_url(
            f"https://discord.com/api/webhooks/1189583746815508510/{src.auth.WEBHOOK}",
            client=self,
        )
        # keep strong ref to heartbeat to avoid gc
        self.hearbeat_task = self.loop.create_task(self.heartbeat_loop())

    async def heartbeat_loop(self):
        if self.in_test:
            return
        if self.is_dev:
            heartbeat_interval = 5
        else:
            heartbeat_interval = 60
        self.log.info("Starting heartbeat")
        while True:
            await asyncio.sleep(heartbeat_interval)
            now_str = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
            self.log.info(
                f"HEARTBEAT: {now_str} tweets: {len(self.snail_state.snail_cache)} fish: {len(self.pond.fishes)} most_recent_message: {self.most_recent_message_id} countdown_cache: {self.countdown_cache}"
            )

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if str(message.channel.type) == "private":
            return

        if not self.activated:
            return

        self.most_recent_message_id = message.id

        # self.fix_tweet(message)
        self.process_message_hooks(message)
        self.cinephile(message)
        # self.tagger(message)
        self.countdown_check(message)
        await self.snail_state.check_snail(message)

    async def _run_event(
        self,
        coro,
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            try:
                await self.on_error(event_name, e, *args, **kwargs)
            except asyncio.CancelledError:
                pass

    async def on_error(
        self, event_method: str, exception: Exception, /, *args: Any, **kwargs: Any
    ) -> None:
        self.log.error(f"Ignoring exception in {event_method}: {str(exception)}")

    def debug(self, message: discord.Message, response: str):
        if self.is_dev:
            self.loop.create_task(message.reply(response))
        else:
            self.log.debug(message)

        return

    def cinephile(self, message):
        src.cinephile.cinema_check(message, self.loop)

    def tagger(self, message: discord.Message):
        if not message.content.startswith("$tag"):
            return

        parsed = src.tagger.parse_tag_command(
            message.content
        )  # help, add, list, alter, delete
        if not parsed:
            self.loop.create_task(
                message.reply(
                    "Sorry, but that tag was not recognized. Try listing tags with $tag list or using $tag help"
                )
            )
            return

        self.debug(message, f"tag: {parsed}")

        match parsed:
            case "help":
                src.tagger.help(message)
            case "add":
                self.add_tag_flow(message)
            case "list":
                self.list_tags(message)
            case "alter":
                return
            case "delete":
                return
            case _:
                self.post_tag(message)

        return

    def _check_tag_abort(self, message: discord.Message):
        abort_id = None
        for id, hook in self.message_hooks.items():
            if hook.owner_id == message.author.id:
                message.reply("Aborting previous tag flow")
                abort_id = id

        if abort_id:
            self.message_hooks.pop(abort_id)
        return

    def add_tag_flow(self, message: discord.Message):
        self._check_tag_abort(message)

        self.message_hooks[message.id] = src.tagger.TagCreationFlow(
            message=message, sql_engine=self.sql_engine, loop=self.loop
        )

    def alter_tag_flow(self, message: discord.Message):
        self._check_tag_abort(message)

        self.message_hooks[message.id] = src.tagger.TagAlterationFlow(message=message)

    async def deactivate(self):
        self.activated = False
        self.snail_state.dump_to_db()
        self.log.info(f"Dumped {len(self.snail_state.snail_cache)} cached snails to db")

    async def activate(self):
        self.snail_state.load_from_db()
        game = discord.Game("Snails | /feedback")
        await self.change_presence(status=discord.Status.online, activity=game)
        self.log.info(
            f"Loaded {len(self.snail_state.snail_cache)} cached snails from db"
        )
        self.activated = True

    def process_message_hooks(self, message: discord.Message):
        cleanup_ids = []
        for id, hook in self.message_hooks.items():
            if hook.owner_id == message.author.id:
                res = hook.next_step(message)
                if res != 0:
                    cleanup_ids.append(id)
                    self.log.info(hook.data)

        for id in cleanup_ids:
            self.message_hooks.pop(id)

    def list_tags(self, message: discord.Message):
        tag_name = message.content.strip().lstrip("$tag list ")
        if tag_name == "":
            embed = src.crud.list_all_tags(self.sql_engine)
        else:
            embed = src.crud.list_tags(tag_name, self.sql_engine)
        self.loop.create_task(message.reply(embed=embed))

    def post_tag(self, message: discord.Message):
        content = message.content.strip().lstrip("$tag ")
        tag = src.crud.get_tag(content, self.sql_engine)

        self.loop.create_task(message.reply(tag))

    def countdown_check(self, message: discord.Message):
        if not message.channel.id == 874290704522821694:
            return

        if not message.content.strip().startswith("<@660689481984376843>"):
            return

        matchli = re.match(r"<@660689481984376843> (\d*)", message.content)
        if not matchli:
            return
        number = int(matchli.group(1))

        if not self.countdown_cache:
            self.countdown_cache = number

        if number > self.countdown_cache:
            self.loop.create_task(message.add_reaction("🤥"))
        else:
            self.countdown_cache = number

    async def get_history(self, channel_id: int, n: int):
        ret_list = []
        channel = self.get_channel(channel_id)
        async for message in channel.history(limit=n):
            reactions_list = []
            for reaction in message.reactions:
                reactions_list.append(
                    src.models.Reaction(
                        emoji_id=str(reaction.emoji), count=reaction.count
                    )
                )
            ret_list.append(
                src.models.Message(
                    author_id=message.author.id,
                    content=message.content,
                    reactions=reactions_list,
                )
            )

        return ret_list
