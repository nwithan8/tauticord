import confuse

class Config:
    def __init__(self, app_name: str, config_path: str):
        self.config = confuse.Configuration(app_name)
        self.config.set_file(filename=config_path)

    @property
    def _tautulli_config(self):
        return self.config['Tautulli']

    @property
    def tautulli_connection_details(self):
        return self._tautulli_config['Connection'].get()

    @property
    def tautulli_customization_details(self):
        return self._tautulli_config['Customization'].get()

    @property
    def tautulli_library_names(self):
        return self._tautulli_config['LibraryNames'].get()

    @property
    def time_settings(self):
        timezone = self.tautulli_customization_details.get('ServerTimeZone', None)
        mil_time = self.tautulli_customization_details.get('Use24HourTime', True)
        return {'timezone': timezone,
                'mil_time': mil_time}

    @property
    def libraries_to_monitor(self):
        return self._tautulli_config['LibraryNames'].get()

    @property
    def _discord_config(self):
        return self.config['Discord']

    @property
    def discord_connection_details(self):
        return self._discord_config['Connection'].get()

    @property
    def discord_customization_details(self):
        return self._discord_config['Customization'].get()

    @property
    def allow_analytics(self):
        return self.config['Extras']['Analytics'].get(bool) == True

    @property
    def log_level(self):
        return self.config['logLevel'].get()