import discord
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
            "No snail contest is open currently", ephemeral=True
        )
        return

    if interaction.user.mention in interaction.client.snail_votes.get("no"):
        await interaction.response.send_message(
            "Sorry but you already voted!", ephemeral=True
        )
        return

    interaction.client.snail_votes.get("yes").add(interaction.user.mention)
    await interaction.response.send_message(
        "Added you to the yes votes", ephemeral=True
    )
    return


@discord.app_commands.command(name="notsnail", description="Vote against snail")
async def no_snail(interaction: discord.Interaction):
    if not interaction.client.snail_lock:
        await interaction.response.send_message(
            "No snail contest is open currently", ephemeral=True
        )
        return

    if interaction.user.mention in interaction.client.snail_votes.get("yes"):
        await interaction.response.send_message(
            "Sorry but you already voted!", ephemeral=True
        )
        return

    interaction.client.snail_votes.get("no").add(interaction.user.mention)
    await interaction.response.send_message("Added you to the no votes", ephemeral=True)
    return


@discord.app_commands.command(name="set_config")
async def set_config(interaction: discord.Interaction, key: str, value: str):
    if interaction.user.name != "karlpopper":
        await interaction.response.send_message("Access denied", ephemeral=True)
        return
    value = str(value)
    key = str(key)

    src.crud.set_config(key, value, interaction.client.sql_engine)
    await interaction.response.send_message("Config set", ephemeral=True)


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


@discord.app_commands.command(name="reset_count")
async def reset_count(interaction: discord.Interaction):
    if interaction.user.name != "karlpopper":
        await interaction.response.send_message("Access denied", ephemeral=True)
        return

    interaction.client.countdown_cache = None
    await interaction.response.send_message(
        "Countdown cache has been reset", ephemeral=True
    )


@discord.app_commands.command(name="sql")
async def sql(interaction: discord.Interaction, sql_string: str):
    if interaction.user.name != "karlpopper":
        engine = interaction.client.sql_engine_ro
    else:
        engine = interaction.client.sql_engine

    try:
        response, col_names = src.crud.raw_sql_execution(sql_string, engine)
        await interaction.response.send_message(
            "Received the following db response:\n" + str(col_names) + "\n" + response
        )
    except Exception as e:
        await interaction.response.send_message("Query failed on db")
        raise e


@discord.app_commands.command(name="set_logging")
async def set_logging(interaction: discord.Interaction, log_level: int):
    if interaction.user.name != "karlpopper":
        await interaction.response.send_message("Access denied", ephemeral=True)
        return

    interaction.client.log.setLevel(log_level)
    await interaction.response.send_message(
        f"Set log level to {log_level}", ephemeral=True
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
    reset_count,
    sql,
    set_logging,
]
