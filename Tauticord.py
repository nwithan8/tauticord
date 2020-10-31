#!/usr/bin/env python3

# Copyright 2020 by Nathan Harris.
# All rights reserved.
# Tauticord is released as-is under the "GNU General Public License".
# Please see the LICENSE file that should have been included as part of this package.

import config as settings
import logging
from modules.logs import *
import modules.tautulli_connector as tautulli
import modules.discord_connector as discord
import modules.analytics as GA

analytics = GA.GoogleAnalytics(analytics_id='UA-174268200-2', anonymous_ip=True,
                               do_not_track=not settings.ALLOW_ANALYTICS)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

session_ids = []

if __name__ == '__main__':
    info("Starting application...")
    t = tautulli.TautulliConnector(base_url=settings.TAUTULLI_URL, api_key=settings.TAUTULLI_API_KEY,
                                   terminate_message=settings.TERMINATE_MESSAGE, analytics=analytics, use_embeds=settings.USE_EMBEDS, plex_pass=settings.PLEX_PASS)
    d = discord.DiscordConnector(token=settings.DISCORD_BOT_TOKEN, owner_id=settings.BOT_OWNER_ID,
                                 refresh_time=settings.REFRESH_TIME, tautulli_channel_id=settings.DISCORD_CHANNEL_ID,
                                 tautulli_connector=t, analytics=analytics, use_embeds=settings.USE_EMBEDS, plex_pass=settings.PLEX_PASS)
    d.connect()
