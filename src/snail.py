import asyncio
import random
import re
import datetime
from dataclasses import dataclass
import discord

import src.datastructures
import src.crud
import src.orm

def check_for_twitter_link(message: str):
    matchli = re.match(r"https://[a-zA-Z]*\.com/.*/status/(\d*)", message)
    if not matchli:
        return False, None
    tweet_id = matchli.group(1)
    return True, tweet_id


def snail_check(message: discord.Message, cache: src.datastructures.LRUCache):
    has_link, tweet_id = check_for_twitter_link(message.content)
    if not has_link:
        return False, None

    cached_item = cache.get(tweet_id)
    if not cached_item:
        cache.put(tweet_id, (message.author.name, datetime.datetime.utcnow()))
        return True, None

    return True, cached_item


def user_mention_to_id(mention: str):

    return int(mention.strip("<@>"))


@dataclass
class CachedXeet:
    tweet_id: str
    initial_poster_name: str
    initial_jump_url: str
    initial_post_time = datetime.datetime.utcnow()
    post_count: int = 1

    def increment_count(self):
        self.post_count += 1

    def describe(self):
        desc = f"This Xeet was first posted by {self.initial_poster_name}. Use this link to jump to their message and check the discussion: {self.initial_jump_url}\n"
        return desc
    
    def to_dict(self):

        return {
            "tweet_id": self.tweet_id,
            "initial_poster_name": self.initial_poster_name,
            "initial_jump_url": self.initial_jump_url,
            "initial_post_time": self.initial_post_time,
            "post_count": self.post_count
        }
    
    @classmethod
    def from_state_cache(cls, snail_cache: src.orm.SnailStateCache):

        return cls(
            tweet_id=snail_cache.tweet_id,
            initial_post_name=snail_cache.initial_poster_name,
            initial_jump_url=snail_cache.initial_jump_url,
            initial_post_time=snail_cache.initial_post_time,
            post_count=snail_cache.post_count
        )


class PollingStation:
    def __init__(self) -> None:
        self.yes_votes = set()
        self.no_votes = set()
        self.registered_voters = set()

    def vote_yes(self, voter_name):
        if voter_name in self.registered_voters:
            return False
        self.yes_votes.add(voter_name)
        self.registered_voters.add(voter_name)
        return True

    def vote_no(self, voter_name):
        if voter_name in self.registered_voters:
            return False
        self.no_votes.add(voter_name)
        self.registered_voters.add(voter_name)
        return True

    def count_ballots(self, is_snail, sql_engine):
        snail_list = []
        if is_snail:
            res = "This xeet was snail!\n"
        else:
            res = "This tweet was not snail!\n"
        if self.registered_voters:
            res += "Exit poll:\n"
        if self.yes_votes:
            res += "Snail Alliance: "
            for voter in self.yes_votes:
                snail_list.append(
                    src.orm.SnailBet(
                        user_id = user_mention_to_id(voter),
                        result = int(is_snail),
                    )
                )
                res += f"{voter} "
            res += "\n"
        if self.no_votes:
            res += "Novelty Coalition: "
            for voter in self.no_votes:
                snail_list.append(
                    src.orm.SnailBet(
                        user_id = user_mention_to_id(voter),
                        result = int(not is_snail),
                    )
                )
                res += f"{voter} "
            res += "\n"
        src.crud.bulk_insert_snail_votes(snail_list, sql_engine)
        return res


class SnailState:
    def __init__(
        self,
        cache_size,
        sql_engine
    ) -> None:
        self.snail_cache = src.datastructures.LRUCache(cache_size)
        self.active_snail_votes: dict[str, PollingStation] = {}
        self.sql_engine = sql_engine

    def vote(self, tweet_id, voter_name, vote_snail):
        polling_station = self.active_snail_votes.get(tweet_id, None)
        if not polling_station:
            return f"Sorry {voter_name}, this vote has already closed"
        if vote_snail:
            is_valid = polling_station.vote_yes(voter_name)
        else:
            is_valid = polling_station.vote_no(voter_name)

        if is_valid:
            return f"Your ballot has been cast successfully"
        else:
            return f"Sorry, your vote has been rejected for suspected ballot stuffing"
    

    def dump_to_db(self):
        caches = [
            xeet.to_dict() for xeet in self.snail_cache.cache.values()
        ]
        if caches:
            src.crud.dump_snail_cache(caches, self.sql_engine)
    

    def load_from_db(self):
        rows = src.crud.load_snail_cache(self.snail_cache.capacity, self.sql_engine)
        for row in reversed(rows):
            cached_xeet = CachedXeet.from_state_cache(row)
            self.snail_cache.put(cached_xeet.tweet_id, cached_xeet)


    async def check_snail(self, message: discord.Message):
        has_link, tweet_id = check_for_twitter_link(message.content)
        if not has_link:
            return

        cached_item = self.snail_cache.get(tweet_id)
        if not cached_item:
            cached_item = CachedXeet(tweet_id, message.author.name, message.jump_url)
            self.snail_cache.put(tweet_id, cached_item)
            if random.random() < 0.95:
                return
            else:
                await self.setup_snailvotes(message, cached_item, False)
                return

        cached_item.increment_count()
        await self.setup_snailvotes(message, cached_item, True)

    async def setup_snailvotes(
        self, message: discord.Message, cached_item: CachedXeet, is_snail: bool
    ):
        if cached_item.tweet_id in self.active_snail_votes.keys():
            await message.reply("You got to be kidding me")
            return
        src.crud.save_snail_vote(message.author.name, is_snail, self.sql_engine)
        self.active_snail_votes[cached_item.tweet_id] = PollingStation()
        reply = await message.reply(
            "Looks like we're due for another snailidental election. You all have 60 seconds to vote!\n",
            view=SnailButtons(tweet_id=cached_item.tweet_id, timeout=60),
        )
        await asyncio.sleep(60)
        reply_content = self.active_snail_votes.pop(cached_item.tweet_id).count_ballots(
            is_snail, self.sql_engine
        )
        edit_content = cached_item.describe()
        if is_snail:
            await reply.edit(content=edit_content, view=None)
        else:
            await reply.delete()
        await message.channel.send(reply_content)


class SnailButtons(discord.ui.View):
    def __init__(self, tweet_id, *, timeout=180):
        super().__init__(timeout=timeout)
        self.tweet_id = tweet_id

    @discord.ui.button(label="Snail!", style=discord.ButtonStyle.red)
    async def snail_button(self, interaction_ctx: discord.Interaction, button_ctx: discord.Button):
        reply = interaction_ctx.client.snail_state.vote(
            self.tweet_id, interaction_ctx.user.mention, True
        )
        await interaction_ctx.response.send_message(reply, ephemeral=True)
        return

    @discord.ui.button(label="Not Snail!", style=discord.ButtonStyle.green)
    async def nosnail_button(self, interaction_ctx: discord.Interaction, button_ctx: discord.Button):
        reply = interaction_ctx.client.snail_state.vote(
            self.tweet_id, interaction_ctx.user.mention, False
        )
        await interaction_ctx.response.send_message(reply, ephemeral=True)
        return
