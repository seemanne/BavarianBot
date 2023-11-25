import asyncio
import random
import logging
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

class Maggus(discord.Client):
    def __init__(self, *, intents: discord.Intents, log: logging.Logger, **options):
        super().__init__(intents=intents, **options)
        self.tree = app_commands.CommandTree(self)
        self.log = log
        self.is_dev = src.auth.DEV

        self.sql_engine = sqlalchemy.create_engine("sqlite:///db/chalkotheke.db")

        self.activated = True
        self.snail_lock = False

        self.message_hooks : dict[int, src.tagger.TagCreationFlow] = {}

        self.fishing_dict = {}
        self.snail_cache = src.snail.LRUCache(1000)
        self.snail_votes = {}

    def __repr__(self) -> str:
        return "BavarianClient"
    
    def __str__(self) -> str:
        return "BavarianClient"

    async def setup_hook(self):

        if self.is_dev:
            guild_id = 143381234494603264
        else:
            guild_id = 389103804835954699

        self.tree.add_command(src.command_tree.start_fishing)
        self.tree.add_command(src.command_tree.reel_fish)
        self.tree.add_command(src.command_tree.yes_snail)
        self.tree.add_command(src.command_tree.no_snail)
        
        self.tree.copy_global_to(guild=discord.Object(id=guild_id))
        await self.tree.sync(guild=discord.Object(id=guild_id))
        self.log.info("COMMAND TREE SYNCED SUCCESSFULLY")
        # This copies the global commands over to your guild.
        #self.tree.copy_global_to(guild=my_secrets.MY_GUILD)
        #await self.tree.sync(guild=my_secrets.MY_GUILD)

    async def on_message(self, message: discord.Message):

        if message.author == self.user:
            return
        
        if(str(message.channel.type) == 'private'): return

        if not self.activated: return

        #self.fix_tweet(message)
        self.process_message_hooks(message)
        self.cinephile(message)
        self.tagger(message)
        await self.snailcheck(message)

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:

        self.log.info('Ignoring exception in %s', event_method)

    def debug(self, message:discord.Message, response: str):

        if self.is_dev:
            self.loop.create_task(message.reply(response))
        else:
            self.log.debug(message)

        return
    
    async def snailcheck(self, message: discord.Message):


        is_x_link, link_info = src.snail.snail_check(message=message, cache=self.snail_cache)
        if not is_x_link:
            return
        if (not link_info and random.random() < 0.8 and not self.is_dev) or self.snail_lock:
            return
        
        if link_info:
            snail=True
        else:
            snail=False
        
        self.snail_lock = True
        await message.reply("Ooooh looks like we're back with another episode of '/snail' or '/notsnail'. You all have 20 seconds to vote!")
        await asyncio.sleep(20)
        
        if snail:
            await message.channel.send(f"It was indeed snail, correct guesses: {self.snail_votes.get('yes')}")
        else:
            await message.channel.send(f"Lol, I tricked you. This Xeet wasn't snail! Correct guesses: {self.snail_votes.get('no')}")
        
        self.snail_votes = {}
        self.snail_lock = False
        


    def cinephile(self, message):

        src.cinephile.cinema_check(message)

    def tagger(self, message: discord.Message):

        if not message.content.startswith("$tag"):
            return
        
        parsed = src.tagger.parse_tag_command(message.content) # help, add, list, alter, delete
        if not parsed:
            self.loop.create_task(message.reply("Sorry, but that tag was not recognized. Try listing tags with $tag list or using $tag help"))
            return
        
        self.debug(message, f"tag: {parsed}")
        
        match parsed:
            case "help": src.tagger.help(message)
            case "add": self.add_tag_flow(message)
            case "list": self.loop.create_task(self.list_tags(message))
            case "alter": return
            case "delete": return
            case _ : self.post_tag(message)

        return
    
    def _check_tag_abort(self, message:discord.Message):

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
        
        self.message_hooks[message.id] = src.tagger.TagCreationFlow(message=message, sql_engine=self.sql_engine)

    def alter_tag_flow(self, message: discord.Message):

        self._check_tag_abort(message)

        self.message_hooks[message.id] = src.tagger.TagAlterationFlow(message=message)
    
    def deactivate(self):

        self.activated = False

    def activate(self):

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
    
    async def list_tags(self, message: discord.Message):

        tag_name = message.content.strip().lstrip("$tag list ")
        if tag_name == "":
            embed = src.crud.list_all_tags(self.sql_engine)
        else:
            embed = src.crud.list_tags(tag_name, self.sql_engine)
        await message.reply(embed = embed)

    def post_tag(self, message: discord.Message):

        content = message.content.strip().lstrip("$tag ")
        tag = src.crud.get_tag(content, self.sql_engine)

        self.loop.create_task(message.reply(tag))

    async def get_history(self, channel_id: int, n: int):

        ret_list = []
        channel = self.get_channel(channel_id)
        async for message in channel.history(limit=n):

            reactions_list = []
            for reaction in message.reactions:
                reactions_list.append(src.models.Reaction(emoji_id=str(reaction.emoji) , count=reaction.count))
            ret_list.append(src.models.Message(author_id=message.author.id, content=message.content, reactions=reactions_list))
        
        return ret_list


#client = Maggus(intents=discord.Intents.all())
#client.run(auth.AUTH)