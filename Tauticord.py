#!/usr/bin/env python3

import config as settings
import logging
from logs import *
import tautulli_connector as tautulli
import discord_connector as discord

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

session_ids = []


if __name__ == '__main__':
    info("Starting application...")
    t = tautulli.TautulliConnector(base_url=settings.TAUTULLI_URL, api_key=settings.TAUTULLI_API_KEY,
                                   terminate_message=settings.TERMINATE_MESSAGE)
    d = discord.DiscordConnector(token=settings.DISCORD_BOT_TOKEN, owner_id=settings.BOT_OWNER_ID,
                                 refresh_time=settings.REFRESH_TIME, tautulli_channel_id=settings.DISCORD_CHANNEL_ID,
                                 tautulli_connector=t)
    d.connect()
