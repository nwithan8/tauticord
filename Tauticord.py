# Copyright 2021 by Nathan Harris.
# All rights reserved.
# Tauticord is released as-is under the "GNU General Public License".
# Please see the LICENSE file that should have been included as part of this package.

from modules import config_parser
from modules.logs import *
import modules.tautulli_connector as tautulli
import modules.discord_connector as discord
import modules.analytics as GA

config = config_parser.Config(app_name="Tauticord", config_path="config.yaml")

analytics = GA.GoogleAnalytics(analytics_id='UA-174268200-2',
                               anonymous_ip=True,
                               do_not_track=not config.allow_analytics)

logging.basicConfig(format='%(levelname)s:%(message)s', level=level_name_to_level(level_name=config.log_level))

if __name__ == '__main__':
    info("Starting application...")
    t = tautulli.TautulliConnector(base_url=config.tautulli_connection_details['URL'],
                                   api_key=config.tautulli_connection_details['APIKey'],
                                   terminate_message=config.tautulli_customization_details.get('TerminateMessage', "Your stream has ended."),
                                   analytics=analytics,
                                   use_embeds=config.discord_customization_details.get('UseEmbeds', True),
                                   plex_pass=config.tautulli_customization_details.get('PlexPass', False),
                                   time_settings=config.time_settings
                                   )
    d = discord.DiscordConnector(token=config.discord_connection_details['BotToken'],
                                 owner_id=config.discord_connection_details['OwnerID'],
                                 refresh_time=config.tautulli_customization_details.get('RefreshSeconds', 15),
                                 tautulli_channel_id=config.discord_connection_details['ChannelID'],
                                 tautulli_connector=t,
                                 analytics=analytics,
                                 use_embeds=config.discord_customization_details.get('UseEmbeds', True)
                                 )
    d.connect()
