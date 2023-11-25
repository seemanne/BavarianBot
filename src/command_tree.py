import discord
import asyncio
import random
import datetime
import logging
import discord.app_commands

LOG = logging.getLogger("uvicorn")


@discord.app_commands.command(name="fish", description="Start fishing in the pond")
async def start_fishing(interaction: discord.Interaction):

    await interaction.response.send_message(f"{interaction.user.name} has started fishing!")
    channel = interaction.channel
    if interaction.client.is_dev:
        seconds = random.randint(1, 60)
    else:
        seconds = random.randint(1, 3600)
    interaction.client.fishing_dict[interaction.user.name] = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
    await asyncio.sleep(seconds)
    await channel.send(f"Looks like {interaction.user.name} caught a fish, quick, /reel it in!")

@discord.app_commands.command(name="reel", description="Reel in your fish")
async def reel_fish(interaction: discord.Interaction):

    timestamp: datetime.datetime = interaction.client.fishing_dict.pop(interaction.user.name, None)
    if not timestamp:
        await interaction.response.send_message(f"Sorry, {interaction.user.name}, it looks like you're not fishing. Why not sit down and /fish ?")
    
    time_diff = abs(timestamp - datetime.datetime.utcnow())
    if  time_diff > datetime.timedelta(seconds=10):

        await interaction.response.send_message(f"Damn, {interaction.user.mention}, it looks like you missed the fish by {time_diff.total_seconds()} seconds!")
    
    await interaction.response.send_message(f"Congratulations, you reeled it in!")

@discord.app_commands.command(name="snail", description="Vote for snail")
async def yes_snail(interaction: discord.Interaction):

    if not interaction.client.snail_lock:
        await interaction.response.send_message (f"No snail contest is open currently", ephemeral=True)
        return
    
    if interaction.user.mention in interaction.client.snail_votes.get("no"):
        await interaction.response.send_message(f"Sorry but you already voted!", ephemeral=True)
        return
    
    interaction.client.snail_votes.get("yes").add(interaction.user.mention)
    await interaction.response.send_message(f"Added you to the yes votes", ephemeral=True)
    return

@discord.app_commands.command(name="notsnail", description="Vote against snail")
async def no_snail(interaction: discord.Interaction):

    if not interaction.client.snail_lock:
        await interaction.response.send_message(f"No snail contest is open currently", ephemeral=True)
        return
    
    if interaction.user.mention in interaction.client.snail_votes.get("yes"):
        await interaction.response.send_message(f"Sorry but you already voted!", ephemeral=True)
        return

    interaction.client.snail_votes.get("no").add(interaction.user.mention)
    await interaction.response.send_message(f"Added you to the no votes", ephemeral=True)
    return

@discord.app_commands.command(name="set_config")
async def set_config(interaction: discord.Interaction, key: str, value: str):

    value = str(value)
    key = str(key)

    src.crud.set_config(key, value, interaction.client.sql_engine)
    await interaction.response.send_message(f"Config set", ephemeral=True)

@discord.app_commands.command(name="get_config")
async def get_config(interaction: discord.Interaction, key: str):

    key = str(key)

    value = src.crud.get_config(key, interaction.client.sql_engine)
    await interaction.response.send_message(f"Key {key} has value {value}", ephemeral=True)



LIST_OF_COMMANDS = [
    start_fishing,
    reel_fish,
    yes_snail,
    no_snail,
    set_config,
    get_config
]