# Copyright 2022, Nathan Harris.
# All rights reserved.
# Tauticord is released as-is under the "GNU General Public License".
# Please see the LICENSE file that should have been included as part of this package.
from pathlib import Path

from modules.analytics import GoogleAnalytics
import modules.discord_connector as discord
import modules.tautulli_connector as tautulli
from modules import config_parser
import modules.logs as logging

config = config_parser.Config(app_name="Tauticord", config_path=f"{Path(Path(__file__).parent / 'config.yaml')}")

analytics = GoogleAnalytics(analytics_id='UA-174268200-2',
                            anonymous_ip=True,
                            do_not_track=not config.extras.allow_analytics)

logging.init(app_name="Tauticord", console_log_level=config.log_level, log_to_file=True)

if __name__ == '__main__':
    logging.info("Starting application...")
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
                                 admin_ids=config.discord.admin_ids,
                                 refresh_time=config.tautulli.refresh_interval,
                                 library_refresh_time=config.tautulli.library_refresh_interval,
                                 tautulli_channel_name=config.discord.channel_name,
                                 tautulli_connector=t,
                                 analytics=analytics,
                                 use_embeds=config.discord.use_embeds,
                                 )
    d.connect()
