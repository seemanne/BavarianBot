import asyncio
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

class Maggus(discord.Client):
    def __init__(self, *, intents: discord.Intents, log: logging.Logger, **options):
        super().__init__(intents=intents, **options)
        self.tree = app_commands.CommandTree(self)
        self.log = log

        self.sql_engine = sqlalchemy.create_engine("sqlite:///chalkotheke.db")

        self.activated = True

        self.message_hooks : dict[int, src.tagger.TagCreationFlow] = {}

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        #self.tree.copy_global_to(guild=my_secrets.MY_GUILD)
        #await self.tree.sync(guild=my_secrets.MY_GUILD)
        pass

    async def on_message(self, message: discord.Message):

        if message.author == self.user:
            return
        
        if(str(message.channel.type) == 'private'): return

        if not self.activated: return

        #self.fix_tweet(message)
        self.process_message_hooks(message)
        self.cinephile(message)
        self.tagger(message)

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:

        self.log.exception('Ignoring exception in %s', event_method)


    def cinephile(self, message):

        src.cinephile.cinema_check(message)

    def tagger(self, message: discord.Message):

        if not message.content.startswith("$tag"):
            return
        
        parsed = src.tagger.parse_tag_command(message.content) # help, add, list, alter, delete
        if not parsed:
            self.loop.create_task(message.reply("Sorry, but that tag was not recognized. Try listing tags with $tag list or using $tag help"))
            return
        
        self.loop.create_task(message.reply(f"tag: {parsed}"))
        
        match parsed:
            case "help": src.tagger.help(message)
            case "add": self.add_tag_flow(message)
            case "list": self.loop.create_task(self.list_tags(message))
            case "alter": return
            case "delete": return
            case _ : self.post_tag(message)

        return
    
    def add_tag_flow(self, message: discord.Message):

        abort_id = None
        for id, hook in self.message_hooks.items():
            if hook.owner_id == message.author.id:
                message.reply("Aborting previous tag creation flow")
                abort_id = id
        
        if abort_id:
            self.message_hooks.pop(abort_id)
            return
        
        self.message_hooks[message.id] = src.tagger.TagCreationFlow(message=message)
    
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
                if res == 1:
                    src.crud.add_tag(hook.data, self.sql_engine)

        for id in cleanup_ids:
            self.message_hooks.pop(id)
    
    async def list_tags(self, message: discord.Message):

        tag_name = message.content.strip().lstrip("$tag list ")
        embed = src.crud.list_tags(tag_name, self.sql_engine)
        await message.reply(embed = embed)

    def post_tag(self, message: discord.Message):

        content = message.content.strip().lstrip("$tag ")
        tag = src.crud.get_tag(content, self.sql_engine)

        self.loop.create_task(message.reply(tag))





def add_bs(engine: sqlalchemy.Engine):

    query = sqlalchemy.insert(src.orm.Config).values(key="test", value="value")

    with engine.connect() as conn:
        conn.execute(query)
        conn.commit()
    
    print("done")



#client = Maggus(intents=discord.Intents.all())
#client.run(auth.AUTH)