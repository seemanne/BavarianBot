from typing import Any
import discord
import discord.app_commands
from discord.interactions import Interaction
import discord.ui as ui
from discord.ui.item import Item


@discord.app_commands.command(name="feedback", description="Give feedback to maggus")
async def feedback(interaction: discord.Interaction):
    modal = SelectView()
    await interaction.response.send_message(view=modal, delete_after=180)


class BugModal(ui.Modal):
    def __init__(self, timeout=180):
        super().__init__(title="Bug report", timeout=timeout)
        self.type = type
        self.add_item(
            ui.TextInput(
                label="What feature is bugged?",
                required=True,
                min_length=0,
                max_length=200,
                style=discord.TextStyle.short,
            )
        )
        self.add_item(
            ui.TextInput(
                label="How did you arrive at the bug?",
                required=True,
                min_length=20,
                max_length=3000,
                style=discord.TextStyle.long,
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="🐛 Bug Report",
            color=discord.Colour.red(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        embed.add_field(
            name="What feature is bugged?", value=self.children[0].value, inline=False
        )
        embed.add_field(
            name="How did you arrive at the bug?",
            value=self.children[1].value,
            inline=False,
        )
        await interaction.client.feedback_webhook.send(embed=embed)
        await interaction.response.send_message(
            "Thank you for submitting this report", ephemeral=True
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.client.on_error(f"Exception in BugReportModal: ", error)


class ImprovementModal(ui.Modal):
    def __init__(self, timeout=180):
        super().__init__(title="Improvement request", timeout=timeout)
        self.type = type
        self.add_item(
            ui.TextInput(
                label="Feature you want improved",
                required=True,
                min_length=0,
                max_length=200,
                style=discord.TextStyle.short,
            )
        )
        self.add_item(
            ui.TextInput(
                label="Describe the changes in detail",
                required=True,
                min_length=20,
                max_length=3000,
                style=discord.TextStyle.long,
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="🚀 Improvement request",
            color=discord.Colour.blue(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        embed.add_field(
            name="Feature you want improved", value=self.children[0].value, inline=False
        )
        embed.add_field(
            name="Describe the changes in detail",
            value=self.children[1].value,
            inline=False,
        )
        await interaction.client.feedback_webhook.send(embed=embed)
        await interaction.response.send_message(
            "Thank you for submitting this report", ephemeral=True
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.client.on_error(f"Exception in ImprovementModal: ", error)


class FeatureRequestModal(ui.Modal):
    def __init__(self, timeout=180):
        super().__init__(title="Feature request", timeout=timeout)
        self.type = type
        self.add_item(
            ui.TextInput(
                label="Describe the feature you want added",
                required=True,
                min_length=20,
                max_length=3000,
                style=discord.TextStyle.long,
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="🚧 Feature Request",
            color=discord.Colour.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        embed.add_field(
            name="Describe the feature you want added",
            value=self.children[0].value,
            inline=False,
        )
        await interaction.client.feedback_webhook.send(embed=embed)
        await interaction.response.send_message(
            "Thank you for submitting this report", ephemeral=True
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.client.on_error(f"Exception in FeatureRequestModal: ", error)


class SelectView(ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(FeedbackTypeSelect())

    async def on_error(
        self, interaction: Interaction, error: Exception, item: Item[Any]
    ) -> None:
        await interaction.client.on_error(f"Feedback SelectView Item: {item}", error)


class FeedbackTypeSelect(ui.Select):
    def __init__(self) -> None:
        option_bug = discord.SelectOption(
            label="Bug",
            value="bug",
            description="Something that seems buggy",
            emoji="🐛",
        )
        option_improvement = discord.SelectOption(
            label="Improvement",
            value="improvement",
            description="An improvement/change to an existing feature",
            emoji="🚀",
        )
        option_feature = discord.SelectOption(
            label="New Feature",
            value="feature",
            description="Suggest a new feature for Maggus",
            emoji="🚧",
        )
        options = [option_bug, option_improvement, option_feature]
        super().__init__(
            placeholder="Type of feedback", min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction) -> Any:
        option = self.values.pop()
        if option == "bug":
            await interaction.response.send_modal(BugModal())
            return
        if option == "improvement":
            await interaction.response.send_modal(ImprovementModal())
            return
        if option == "feature":
            await interaction.response.send_modal(FeatureRequestModal())
            return

        raise KeyError(f"FeedbackSelect callback returned invalid option {option}")
