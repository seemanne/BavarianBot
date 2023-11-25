import discord
import discord.app_commands
import datetime
import random
import asyncio

FISHING_REACTION_SECONDS=60

@discord.app_commands.command(name="fish", description="Start fishing in the pond")
async def start_fishing(interaction: discord.Interaction):

    await interaction.response.send_message(f"{interaction.user.name} has started fishing!")
    channel = interaction.channel
    if interaction.client.is_dev:
        seconds = random.randint(1, 60)
    else:
        seconds = random.randint(1, 3600)
    
    current_fish_timestamp = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
    interaction.client.pond.add_fisher(interaction.user.name, current_fish_timestamp)
    await asyncio.sleep(seconds)
    is_there, _ = interaction.client.pond.get_fisher(interaction.user.name)
    if is_there:
        await channel.send(f"Looks like a fish is biting your rod {interaction.user.name}, quick, /reel it in!")
    else:
        await channel.send(f"{interaction.user.name}, your fish just showed up, but you already tried to /reel it. What a loser!")
    await asyncio.sleep(FISHING_REACTION_SECONDS)
    # cheap hack to check if they failed to fish: if they are still at the pond and the timestamp is the same
    is_there, possibly_different_timestamp = interaction.client.pond.get_fisher(interaction.user.name)
    if is_there and current_fish_timestamp == possibly_different_timestamp:
        fish = interaction.client.pond.get_fish()
        additional_weight = fish.feed()
        interaction.client.pond.return_fish(fish)
        await channel.send(f"{interaction.user.mention} failed to catch their fish. The fish enjoyed the snack and is now {additional_weight}g heavier.")


@discord.app_commands.command(name="reel", description="Reel in your fish")
async def reel_fish(interaction: discord.Interaction):

    is_there, timestamp = interaction.client.pond.get_fisher(interaction.user.name)
    if not is_there:
        await interaction.response.send_message(f"Sorry, {interaction.user.name}, it looks like you're not fishing. Why not sit down and /fish ?")
        return
    
    time_diff = abs(timestamp - datetime.datetime.utcnow())
    if  time_diff > datetime.timedelta(seconds=FISHING_REACTION_SECONDS):

        await interaction.response.send_message(f"Damn, {interaction.user.mention}, it looks like you missed the fish by {time_diff.total_seconds()} seconds!")
        return
    
    fish = interaction.client.pond.get_fish()
    interaction.client.pond.refill_fish()
    await interaction.response.send_message(fish.get_catch_message(interaction.user.mention))