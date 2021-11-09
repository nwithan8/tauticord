import confuse
import os

class Config:
    def __init__(self, app_name: str, config_path: str):
        self.config = confuse.Configuration(app_name)
        self.config.set_file(filename=config_path)

    @property
    def _tautulli_config(self):
        return self.config['Tautulli']

    @property
    def tautulli_connection_details(self):
        configfile = self._tautulli_config['Connection'].get()
        if os.getenv("TAUTULLI_IP"):
            configfile['URL'] = bool(os.getenv("TAUTULLI_IP"))
        if os.getenv("TAUTULLI_API_KEY"):
            configfile['APIKey'] = os.getenv("TAUTULLI_API_KEY")
        return configfile

    @property
    def tautulli_customization_details(self):
        configfile = self._tautulli_config['Customization'].get()
        if os.getenv("TC_PLEXPASS"):
            configfile['PlexPass'] = bool(os.getenv("TC_PLEXPASS"))
        if os.getenv("TC_REFRESH_SEC"):
            configfile['RefreshSeconds'] = int(os.getenv("TC_REFRESH_SEC"))
        return configfile

    @property
    def tautulli_voice_channels(self):
        configfile = self._tautulli_config['Customization']['VoiceChannels'].get()
        if os.getenv("TC_CHANNELS"):
            channels = os.getenv("TC_CHANNELS").split(",")
            for i in range(len(channels)):
                channels[i] = channels[i] in ("true","True","1")
            configfile['StreamCount'] = channels[0]
            configfile['TranscodeCount'] = channels[1]
            configfile['Bandwidth'] = channels[2]
            configfile['LibraryStats'] = channels[3]
        if os.getenv("TC_LIBRARY"):
            configfile['LibraryNames'] = os.getenv("TC_LIBRARY").split(",")
        return configfile

    @property
    def time_settings(self):
        timezone = self.tautulli_customization_details.get('ServerTimeZone', None)
        mil_time = self.tautulli_customization_details.get('Use24HourTime', True)
        return {'timezone': timezone,
                'mil_time': mil_time}

    @property
    def voice_channels(self):
        _settings = self.tautulli_voice_channels
        return {
            'count': _settings.get('StreamCount', False),
            'transcodes': _settings.get('TranscodeCount', False),
            'bandwidth': _settings.get('Bandwidth', False),
            'stats': _settings.get('LibraryStats', False),
            'libraries': _settings.get('LibraryNames', [])
        }

    @property
    def _discord_config(self):
        return self.config['Discord']

    @property
    def discord_connection_details(self):
        configfile = self._discord_config['Connection'].get()
        if os.getenv("TC_DISCORD_BOT_TOKEN"):
            configfile['BotToken'] = os.getenv("TC_DISCORD_BOT_TOKEN")
        if os.getenv("TC_DISCORD_SERVER_ID"):
            configfile['ServerID'] = int(os.getenv("TC_DISCORD_SERVER_ID"))
        if os.getenv("TC_DISCORD_OWNER_ID"):
            configfile['OwnerID'] = int(os.getenv("TC_DISCORD_OWNER_ID"))
        if os.getenv("TC_DISCORD_CHANNELNAME"):
            configfile['ChannelName'] = os.getenv("TC_DISCORD_CHANNELNAME")
        return configfile

    @property
    def discord_customization_details(self):
        configfile = self._discord_config['Customization'].get()
        if os.getenv("TC_DISCORD_USEEMBEDS"):
            configfile['ChannelName'] = os.getenv("TC_DISCORD_CHANNELNAME")
        return configfile

    @property
    def allow_analytics(self):
        if os.getenv("TC_ANALYTICS"):
            return bool(os.getenv("TAUTULLI_IP"))
        return self.config['Extras']['Analytics'].get(bool) == True

    @property
    def log_level(self):
        return self.config['logLevel'].get()