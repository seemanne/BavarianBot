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
    interaction.client.fishing_dict[interaction.user.name] = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
    await asyncio.sleep(seconds)
    if interaction.user.name in interaction.client.fishing_dict:
        await channel.send(f"Looks like a fish is biting your rod {interaction.user.name}, quick, /reel it in!")
    else:
        await channel.send(f"{interaction.user.name}, your fish just showed up, but you already tried to /reel it. What a loser!")

@discord.app_commands.command(name="reel", description="Reel in your fish")
async def reel_fish(interaction: discord.Interaction):

    timestamp: datetime.datetime = interaction.client.fishing_dict.pop(interaction.user.name, None)
    if not timestamp:
        await interaction.response.send_message(f"Sorry, {interaction.user.name}, it looks like you're not fishing. Why not sit down and /fish ?")
    
    time_diff = abs(timestamp - datetime.datetime.utcnow())
    if  time_diff > datetime.timedelta(seconds=FISHING_REACTION_SECONDS):

        await interaction.response.send_message(f"Damn, {interaction.user.mention}, it looks like you missed the fish by {time_diff.total_seconds()} seconds!")
    
    await interaction.response.send_message(f"Congratulations, you reeled it in!")