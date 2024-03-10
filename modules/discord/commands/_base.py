import discord


async def respond_thinking(interaction: discord.Interaction, ephemeral: bool = True) -> None:
    await interaction.response.defer(thinking=True, ephemeral=ephemeral)
