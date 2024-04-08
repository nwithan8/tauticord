import discord
from discord.ext import commands

import modules.logs as logging
from modules.discord.commands import (
    Most,
    Summary,
    Recently,
)
from modules.discord.services.base_service import BaseService
from modules.emojis import EmojiManager
from modules.tautulli.tautulli_connector import TautulliConnector


class SlashCommandManager(BaseService):
    """
    A service that manages slash commands for the Discord bot. Starts running when the bot is ready.
    """

    def __init__(self, enable_slash_commands: bool, guild_id: int, tautulli: TautulliConnector,
                 emoji_manager: EmojiManager, admin_ids: list[int] = None):
        super().__init__()
        self._enable_slash_commands = enable_slash_commands
        self._guild_id = guild_id
        self._admin_ids = admin_ids or []
        self._tautulli = tautulli
        self._emoji_manager = emoji_manager
        self._synced = False

    async def enabled(self) -> bool:
        return True  # Always enabled, because need to sync slash commands regardless

    async def on_ready(self):
        if self._enable_slash_commands:
            for cog in self._cogs_to_add:
                await self._add_cog(cog)
            logging.info("Slash commands registered.")
        else:
            logging.info("Slash commands not enabled. Skipping registration...")

        # Need to sync regardless (either adding newly-registered cogs or syncing/removing existing ones)
        logging.info("Syncing slash commands...")
        if not self._synced:
            await self.bot.tree.sync(guild=self._guild)
            self._synced = True
            logging.info("Slash commands synced.")
        else:
            logging.info("Slash commands already synced.")

    @property
    def _cogs_to_add(self):
        return [
            Most(bot=self.bot, tautulli=self._tautulli, admin_check=self.is_admin),
            Summary(bot=self.bot, tautulli=self._tautulli, emoji_manager=self._emoji_manager,
                    admin_check=self.is_admin),
            Recently(bot=self.bot, tautulli=self._tautulli, admin_check=self.is_admin),
        ]

    @property
    def _active_cogs(self):
        return self.bot.cogs

    @property
    def _guild(self):
        return discord.Object(id=self._guild_id)

    async def _add_cog(self, cog: commands.Cog):
        await self.bot.add_cog(cog, guild=self._guild)

    def is_admin(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id in self._admin_ids
