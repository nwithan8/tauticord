# Copyright 2022, Nathan Harris.
# All rights reserved.
# Tauticord is released as-is under the "GNU General Public License".
# Please see the LICENSE file that should have been included as part of this package.

from modules.analytics import GoogleAnalytics
import modules.discord_connector as discord
import modules.tautulli_connector as tautulli
from modules import config_parser
from modules.logs import *

config = config_parser.Config(app_name="Tauticord", config_path="config.yaml")

analytics = GoogleAnalytics(analytics_id='UA-174268200-2',
                            anonymous_ip=True,
                            do_not_track=not config.extras.allow_analytics)

logging.basicConfig(format='%(levelname)s:%(message)s', level=level_name_to_level(level_name=config.log_level))

if __name__ == '__main__':
    info("Starting application...")
    t = tautulli.TautulliConnector(base_url=config.tautulli.url,
                                   api_key=config.tautulli.api_key,
                                   terminate_message=config.tautulli.terminate_message,
                                   analytics=analytics,
                                   use_embeds=config.discord.use_embeds,
                                   plex_pass=config.tautulli.has_plex_pass,
                                   voice_channel_settings=config.tautulli.voice_channel_settings,
                                   time_settings=config.tautulli.time_settings
                                   )
    d = discord.DiscordConnector(token=config.discord.bot_token,
                                 guild_id=config.discord.server_id,
                                 owner_id=config.discord.owner_id,
                                 refresh_time=config.tautulli.refresh_interval,
                                 tautulli_channel_name=config.discord.channel_name,
                                 tautulli_connector=t,
                                 analytics=analytics,
                                 use_embeds=config.discord.use_embeds,
                                 )
    d.connect()
