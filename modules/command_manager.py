import discord
from discord.ext import commands

import modules.logs as logging
from modules.commands.top import Top
from modules.tautulli_connector import TautulliConnector


class CommandManager:
    def __init__(self,
                 bot: commands.Bot,
                 guild_id: str,
                 tautulli: TautulliConnector,
                 admin_ids: list[str] = None):
        self._bot = bot
        self._guild_id = guild_id
        self._admin_ids = admin_ids or []
        self._tautulli = tautulli
        self._synced = False

    @property
    def _guild(self):
        return discord.Object(id=self._guild_id)

    def is_admin(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) in self._admin_ids

    async def register_slash_commands(self):
        await self._bot.add_cog(
            Top(
                bot=self._bot, tautulli=self._tautulli
            ),
            guild=self._guild
        )

        logging.info("Slash commands registered.")

    async def activate_slash_commands(self):
        if not self._synced:
            await self._bot.tree.sync(guild=self._guild)
            self._synced = True
            logging.info("Slash commands activated.")
        else:
            logging.info("Slash commands already activated.")
