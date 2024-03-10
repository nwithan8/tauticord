import discord
from discord.ext import commands

import modules.logs as logging
from modules.discord.commands import (
    Most,
    Summary,
    Recently,
)
from modules.emojis import EmojiManager
from modules.tautulli.tautulli_connector import TautulliConnector


class CommandManager:
    def __init__(self,
                 enable_slash_commands: bool,
                 bot: commands.Bot,
                 guild_id: str,
                 tautulli: TautulliConnector,
                 emoji_manager: EmojiManager,
                 admin_ids: list[str] = None):
        self._enable_slash_commands = enable_slash_commands
        self._bot = bot
        self._guild_id = guild_id
        self._admin_ids = admin_ids or []
        self._tautulli = tautulli
        self._emoji_manager = emoji_manager
        self._synced = False

    @property
    def _cogs_to_add(self):
        return [
            Most(bot=self._bot, tautulli=self._tautulli, admin_check=self.is_admin),
            Summary(bot=self._bot, tautulli=self._tautulli, emoji_manager=self._emoji_manager, admin_check=self.is_admin),
            Recently(bot=self._bot, tautulli=self._tautulli, admin_check=self.is_admin),
        ]

    @property
    def _active_cogs(self):
        return self._bot.cogs

    @property
    def _guild(self):
        return discord.Object(id=self._guild_id)

    async def _add_cog(self, cog: commands.Cog):
        await self._bot.add_cog(cog, guild=self._guild)

    def is_admin(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) in self._admin_ids

    async def register_slash_commands(self):
        for cog in self._cogs_to_add:
            await self._add_cog(cog)

        logging.info("Slash commands registered.")

    async def activate_slash_commands(self):
        if not self._enable_slash_commands:
            logging.info("Slash commands not enabled. Skipping activation.")
            return

        if not self._synced:
            await self._bot.tree.sync(guild=self._guild)
            self._synced = True
            logging.info("Slash commands activated.")
        else:
            logging.info("Slash commands already activated.")
