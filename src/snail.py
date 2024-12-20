import asyncio
import random
import re
import datetime
from dataclasses import dataclass
import logging
import discord

import src.datastructures
import src.crud
import src.orm
import src.auth
import src.images.needle

LOG = logging.getLogger("uvicorn")


def check_for_twitter_link(message: str):
    matchli = re.search(r"https://[a-zA-Z]*\.com/.*/status/(\d*)", message)
    if not matchli:
        return False, None
    tweet_id = matchli.group(1)
    return True, tweet_id


def check_for_bluesky_link(message: str):
    matchli = re.search(r"bsky\.app/profile/(.*)/post/([^?]*)", message)
    if not matchli:
        return False, None
    bsky_id = f"{matchli.group(1)}-{matchli.group(2)}"
    return True, bsky_id


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
        desc = f"This piece of content was first posted by {self.initial_poster_name}. Use this link to jump to their message and check the discussion: {self.initial_jump_url}"
        return desc

    def to_dict(self):
        return {
            "tweet_id": self.tweet_id,
            "initial_poster_name": self.initial_poster_name,
            "initial_jump_url": self.initial_jump_url,
            "initial_post_time": self.initial_post_time,
            "post_count": self.post_count,
        }

    @classmethod
    def from_state_cache(cls, snail_cache: src.orm.SnailStateCache):
        ret = cls(
            tweet_id=snail_cache.tweet_id,
            initial_poster_name=snail_cache.initial_poster_name,
            initial_jump_url=snail_cache.initial_jump_url,
        )
        ret.initial_post_time = snail_cache.initial_post_time
        ret.post_count = snail_cache.post_count
        return ret


class PollingStation:
    def __init__(self) -> None:
        self.yes_votes = list()
        self.no_votes = list()
        self.registered_voters = set()
        self.open = True
        self.needle_message: discord.Message = None
        self.has_needle = False
        self.never_needle = False
        self.last_needle_update = datetime.datetime.now(datetime.UTC)
        self.last_needle_update_token = 0
        self.task_collector = set()  # holds strong references to tasks to avoid gc

    async def handover_reply(self, reply):
        self.needle_message = reply
        await self.update_needle()

    async def close(self):
        self.open = False
        if self.has_needle:
            await asyncio.sleep(3)

    def n_ballots_received(self):
        return len(self.no_votes) + len(self.yes_votes)

    async def update_needle(self): # pragma: no cover
        # we need to stay within the 1 edit per second limit, but votes come in concurrently
        if self.never_needle:
            return
        if not self.has_needle and random.random() > 0.5 and not src.auth.DEV:
            LOG.debug("Lost needle roll")
            self.never_needle = True
            return

        if not self.has_needle:
            self.has_needle = True
            LOG.debug("Starting needling")

        if not self.needle_message:
            # rare case where we have not been handed the reply yet
            LOG.warning("Needle update called but needle was not passed yet")
            await asyncio.sleep(0.5)
            await self.update_needle()

        if self.last_needle_update > datetime.datetime.now(
            datetime.UTC
        ) - datetime.timedelta(seconds=2):
            LOG.debug("Bounced update (too soon)")
            token = self.last_needle_update_token
            await asyncio.sleep(2)
            if token == self.last_needle_update_token:
                LOG.debug("Update redrive triggered")
                await self.update_needle()
            return

        self.last_needle_update_token += 1
        self.last_needle_update = datetime.datetime.now(datetime.UTC)
        await self._update_needle()

    async def _update_needle(self):
        LOG.debug("Triggered an update for needle")
        net_score = len(self.yes_votes) - len(self.no_votes)

        buffer = src.images.needle.get_needle_into_buffer(net_score)
        file = discord.File(buffer, "snail_needle.png")
        await self.needle_message.edit(attachments=[file])
        buffer.close()

    def vote_yes(self, voter_name):
        if voter_name in self.registered_voters and not src.auth.DEV:
            return False
        self.yes_votes.append(voter_name)
        self.registered_voters.add(voter_name)
        self.task_collector.add(asyncio.create_task(self.update_needle()))
        return True

    def vote_no(self, voter_name):
        if voter_name in self.registered_voters and not src.auth.DEV:
            return False
        self.no_votes.append(voter_name)
        self.registered_voters.add(voter_name)
        self.task_collector.add(asyncio.create_task(self.update_needle()))
        return True

    def count_ballots(self, is_snail, sql_engine):
        LOG.debug("Counting ballots")
        snail_list = []
        if not is_snail:
            res = "This post was not snail!\n"
        else:
            res = "\n"
        if self.registered_voters:
            res += "Exit poll:\n"
        if self.yes_votes:
            res += "Snail Alliance: "
            for voter in self.yes_votes:
                snail_list.append(
                    src.orm.SnailBet(
                        user_id=user_mention_to_id(voter),
                        result=int(is_snail),
                    )
                )
                res += f"{voter} "
            res += "\n"
        if self.no_votes:
            res += "Novelty Coalition: "
            for voter in self.no_votes:
                snail_list.append(
                    src.orm.SnailBet(
                        user_id=user_mention_to_id(voter),
                        result=int(not is_snail),
                    )
                )
                res += f"{voter} "
            res += "\n"
        if snail_list:
            src.crud.bulk_insert_snail_votes(snail_list, sql_engine)
        return res


class LinkChecker:
    def __init__(self) -> None:
        self.rules_to_check = [
            check_for_twitter_link,
            check_for_bluesky_link,
        ]

    def check_message(self, message: str):
        if "https://" not in message:
            return False, None

        for rule in self.rules_to_check:
            matched, res = rule(message)
            if matched:
                return matched, res
        return False, None


class SnailState:
    def __init__(self, cache_size, sql_engine) -> None:
        self.snail_cache = src.datastructures.LRUCache(cache_size)
        self.active_snail_votes: dict[str, PollingStation] = {}
        self.link_checker = LinkChecker()
        self.sql_engine = sql_engine

    def vote(self, tweet_id, voter_name, vote_snail):
        polling_station = self.active_snail_votes.get(tweet_id, None)
        if not polling_station:
            return f"Sorry {voter_name}, this vote has already closed"
        if not polling_station.open:
            return f"Sorry {voter_name}, looks like you didn't reach the polling station in time"
        if vote_snail:
            is_valid = polling_station.vote_yes(voter_name)
        else:
            is_valid = polling_station.vote_no(voter_name)

        if is_valid:
            return "Your ballot has been cast successfully"
        else:
            return "Sorry, your vote has been rejected for suspected ballot stuffing"

    def dump_to_db(self):
        caches = [xeet.to_dict() for xeet in self.snail_cache.cache.values()]
        if caches:
            src.crud.dump_snail_cache(caches, self.sql_engine)

    def load_from_db(self):
        rows = src.crud.load_snail_cache(self.snail_cache.capacity, self.sql_engine)
        for row in reversed(rows):
            cached_xeet = CachedXeet.from_state_cache(row)
            self.snail_cache.put(cached_xeet.tweet_id, cached_xeet)

    async def check_snail(self, message: discord.Message):
        if "https://" not in message.content:
            return
        has_post, post_id = self.link_checker.check_message(message.content)
        if not has_post:
            return

        cached_item = self.snail_cache.get(post_id)
        if not cached_item:
            cached_item = CachedXeet(post_id, message.author.name, message.jump_url)
            self.snail_cache.put(post_id, cached_item)
            LOG.debug(f"Post detected new with id: {post_id}")
            if random.random() < 0.95:
                return
            else:
                await self.setup_snailvotes(message, cached_item, False)
                return

        if message.reference:
            LOG.debug("Bailing on snailvote due to reply")
            await message.reply("This message is snail, but I will let it fly")
            return
        cached_item.increment_count()
        LOG.debug(f"Post detected snail with id: {post_id}")
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
        await self.active_snail_votes[cached_item.tweet_id].handover_reply(reply)
        LOG.debug("Completed reply handover to PollingStation")
        await asyncio.sleep(60)

        if self.active_snail_votes.get(cached_item.tweet_id).n_ballots_received() >= 3:
            await asyncio.sleep(30)

        LOG.debug("Closing snailvote")
        await self.active_snail_votes.get(cached_item.tweet_id).close()

        reply_content = self.active_snail_votes.pop(cached_item.tweet_id).count_ballots(
            is_snail, self.sql_engine
        )
        edit_content = cached_item.describe()
        LOG.debug("Posting snailresults")
        if is_snail:
            await reply.edit(content=edit_content + reply_content, view=None)
        else:
            await reply.edit(content=reply_content, view=None)


class SnailButtons(discord.ui.View):
    def __init__(self, tweet_id, *, timeout=180):
        super().__init__(timeout=timeout)
        self.tweet_id = tweet_id

    @discord.ui.button(label="Snail!", style=discord.ButtonStyle.red)
    async def snail_button(
        self, interaction_ctx: discord.Interaction, button_ctx: discord.Button
    ):
        reply = interaction_ctx.client.snail_state.vote(
            self.tweet_id, interaction_ctx.user.mention, True
        )
        await interaction_ctx.response.send_message(
            reply, ephemeral=True, delete_after=7
        )
        return

    @discord.ui.button(label="Not Snail!", style=discord.ButtonStyle.green)
    async def nosnail_button(
        self, interaction_ctx: discord.Interaction, button_ctx: discord.Button
    ):
        reply = interaction_ctx.client.snail_state.vote(
            self.tweet_id, interaction_ctx.user.mention, False
        )
        await interaction_ctx.response.send_message(
            reply, ephemeral=True, delete_after=7
        )
        return
