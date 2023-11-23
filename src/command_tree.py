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
        await interaction.response.send_message(f"No snail contest is open currently", ephemeral=True)
    
    interaction.client.snail_votes["yes"] = interaction.client.snail_votes.get("yes", []) + [interaction.user.mention]
    await interaction.response.send_message(f"Added you to the yes votes", ephemeral=True)

@discord.app_commands.command(name="notsnail", description="Vote against snail")
async def no_snail(interaction: discord.Interaction):

    if not interaction.client.snail_lock:
        await interaction.response.send_message(f"No snail contest is open currently", ephemeral=True)
    
    interaction.client.snail_votes["no"] = interaction.client.snail_votes.get("no", []) + [interaction.user.mention]
    await interaction.response.send_message(f"Added you to the no votes", ephemeral=True)