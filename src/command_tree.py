import discord
import asyncio
import random
import datetime
import logging
import discord.app_commands
import src.crud

from src.fishing.commands import reel_fish, start_fishing, get_rod
from src.feedback.commands import feedback


async def on_error(
    interaction: discord.Interaction, error: discord.app_commands.AppCommandError
):
    interaction.client.log.info(
        f"Error when calling {interaction.command.name}: {error}"
    )


@discord.app_commands.command(name="snail", description="Vote for snail")
async def yes_snail(interaction: discord.Interaction):
    if not interaction.client.snail_lock:
        await interaction.response.send_message(
            f"No snail contest is open currently", ephemeral=True
        )
        return

    if interaction.user.mention in interaction.client.snail_votes.get("no"):
        await interaction.response.send_message(
            f"Sorry but you already voted!", ephemeral=True
        )
        return

    interaction.client.snail_votes.get("yes").add(interaction.user.mention)
    await interaction.response.send_message(
        f"Added you to the yes votes", ephemeral=True
    )
    return


@discord.app_commands.command(name="notsnail", description="Vote against snail")
async def no_snail(interaction: discord.Interaction):
    if not interaction.client.snail_lock:
        await interaction.response.send_message(
            f"No snail contest is open currently", ephemeral=True
        )
        return

    if interaction.user.mention in interaction.client.snail_votes.get("yes"):
        await interaction.response.send_message(
            f"Sorry but you already voted!", ephemeral=True
        )
        return

    interaction.client.snail_votes.get("no").add(interaction.user.mention)
    await interaction.response.send_message(
        f"Added you to the no votes", ephemeral=True
    )
    return


@discord.app_commands.command(name="set_config")
async def set_config(interaction: discord.Interaction, key: str, value: str):

    if interaction.user.name != "karlpopper":
        await interaction.response.send_message("Access denied", ephemeral=True)
        return
    value = str(value)
    key = str(key)

    src.crud.set_config(key, value, interaction.client.sql_engine)
    await interaction.response.send_message(f"Config set", ephemeral=True)


@discord.app_commands.command(name="get_config")
async def get_config(interaction: discord.Interaction, key: str):

    if interaction.user.name != "karlpopper":
        await interaction.response.send_message("Access denied", ephemeral=True)
        return
    key = str(key)

    value = src.crud.get_config(key, interaction.client.sql_engine)
    await interaction.response.send_message(
        f"Key {key} has value {value}", ephemeral=True
    )


LIST_OF_COMMANDS = [
    start_fishing,
    reel_fish,
    yes_snail,
    no_snail,
    set_config,
    get_config,
    get_rod,
    feedback,
]
