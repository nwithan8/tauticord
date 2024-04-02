import json
import os
from typing import Any

import yaml

import modules.logs as logging
import modules.settings.models as settings_models
from modules import utils
from modules.emojis import Emoji
from modules.statics import KEY_RUN_ARGS_MONITOR_PATH, KEY_RUN_ARGS_CONFIG_PATH, KEY_RUN_ARGS_LOG_PATH


class ConfigSection:
    def __init__(self, data: dict):
        self.data = data

    def get_value(self, key: str, default: Any = None) -> Any:
        try:
            return self.data[key]
        except KeyError:
            return default

    def get_subsection_data(self, key: str) -> dict:
        try:
            data = self.data[key]
            assert isinstance(data, dict)
            return data
        except KeyError:
            raise KeyError(f"Subsection '{key}' not found in section")


class VoiceChannelConfig(ConfigSection):
    def __init__(self, channel_name: str, emoji: Emoji, data):
        super().__init__(data=data)
        self.channel_name = channel_name
        self.emoji = emoji

    def to_model(self) -> settings_models.VoiceChannel:
        enable: bool = utils.extract_boolean(self.get_value(key="Enable", default=False))
        name: str = self.get_value(key="CustomName", default="")
        if not name:
            # Fall back to the default channel name if a custom name is not provided
            name: str = self.channel_name
        emoji: str = self.get_value(key="CustomEmoji", default="")
        if not emoji:
            # Fall back to the default emoji if a custom emoji is not provided
            emoji: str = self.emoji.value  # type: ignore
        channel_id: int = self.get_value(key="VoiceChannelID", default="0")

        return settings_models.VoiceChannel(
            name=name.strip(),
            enable=enable,
            emoji=emoji.strip(),
            channel_id=channel_id
        )


class DiscordConfig(ConfigSection):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def to_model(self) -> settings_models.Discord:
        bot_token = self.get_value(key="BotToken")
        server_id = self.get_value(key="ServerID")
        admin_ids = self.get_value(key="AdminIDs", default=[])
        channel_name = self.get_value(key="ChannelName", default="tauticord")
        channel_name = utils.discord_text_channel_name_format(string=channel_name)
        use_summary_message = utils.extract_boolean(self.get_value(key="PostSummaryMessage", default=True))
        enable_slash_commands = utils.extract_boolean(self.get_value(key="EnableSlashCommands", default=False))

        return settings_models.Discord(
            bot_token=bot_token,
            server_id=server_id,
            admin_ids=admin_ids,
            channel_name=channel_name,
            use_summary_message=use_summary_message,
            enable_slash_commands=enable_slash_commands,
        )


class AnonymityConfig(ConfigSection):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def to_model(self) -> settings_models.Anonymity:
        hide_usernames = utils.extract_boolean(self.get_value(key="HideUsernames", default=False))
        hide_platforms = utils.extract_boolean(self.get_value(key="HidePlatforms", default=False))
        hide_player_names = utils.extract_boolean(self.get_value(key="HidePlayerNames", default=False))
        hide_quality = utils.extract_boolean(self.get_value(key="HideQuality", default=False))
        hide_bandwidth = utils.extract_boolean(self.get_value(key="HideBandwidth", default=False))
        hide_transcode_decision = utils.extract_boolean(self.get_value(key="HideTranscode", default=False))
        hide_progress = utils.extract_boolean(self.get_value(key="HideProgress", default=False))
        hide_eta = utils.extract_boolean(self.get_value(key="HideETA", default=False))

        return settings_models.Anonymity(
            hide_usernames=hide_usernames,
            hide_platforms=hide_platforms,
            hide_player_names=hide_player_names,
            hide_quality=hide_quality,
            hide_bandwidth=hide_bandwidth,
            hide_transcode_decision=hide_transcode_decision,
            hide_progress=hide_progress,
            hide_eta=hide_eta,
        )


class TimeConfig(ConfigSection):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def to_model(self) -> settings_models.Time:
        tautulli_server_time_zone = self.get_value(key="ServerTimeZone", default="UTC")
        use_24_hour_time = utils.extract_boolean(self.get_value(key="Use24HourTime", default=False))

        return settings_models.Time(
            tautulli_server_time_zone=tautulli_server_time_zone,
            use_24_hour_time=use_24_hour_time
        )


class DisplayConfig(ConfigSection):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def to_model(self) -> settings_models.Display:
        anonymity = AnonymityConfig(data=self.get_subsection_data(key="Anonymize")).to_model()
        plex_server_name = self.get_value(key="ServerName", default="Plex Server")
        thousands_separator = self.get_value(key="ThousandsSeparator", default="")
        time = TimeConfig(data=self.get_subsection_data(key="Time")).to_model()
        use_friendly_names = utils.extract_boolean(self.get_value(key="UseFriendlyNames", default=False))

        return settings_models.Display(
            anonymity=anonymity,
            plex_server_name=plex_server_name,
            thousands_separator=thousands_separator,
            time=time,
            use_friendly_names=use_friendly_names
        )


class ExtrasConfig(ConfigSection):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def to_model(self) -> settings_models.Extras:
        allow_analytics = utils.extract_boolean(self.get_value(key="AllowAnalytics", default=True))
        enable_update_reminders = utils.extract_boolean(self.get_value(key="EnableUpdateReminders", default=True))

        return settings_models.Extras(
            allow_analytics=allow_analytics,
            update_reminders=enable_update_reminders
        )


class StatsActivityConfig(ConfigSection):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def to_model(self) -> settings_models.ActivityStats:
        category_name = self.get_value(key="CategoryName", default="Plex Activity")
        enable = utils.extract_boolean(self.get_value(key="Enable", default=False))

        stats_types = ConfigSection(data=self.get_subsection_data(key="StatTypes"))
        bandwidth = VoiceChannelConfig(channel_name="Bandwidth",
                                       emoji=Emoji.Bandwidth,
                                       data=stats_types.get_subsection_data("Bandwidth")).to_model()
        local_bandwidth = VoiceChannelConfig(channel_name="Local Bandwidth",
                                             emoji=Emoji.LocalBandwidth,
                                             data=stats_types.get_subsection_data("LocalBandwidth")).to_model()
        remote_bandwidth = VoiceChannelConfig(channel_name="Remote Bandwidth",
                                              emoji=Emoji.RemoteBandwidth,
                                              data=stats_types.get_subsection_data("RemoteBandwidth")).to_model()
        stream_count = VoiceChannelConfig(channel_name="Stream Count",
                                          emoji=Emoji.Stream,
                                          data=stats_types.get_subsection_data("StreamCount")).to_model()
        transcode_count = VoiceChannelConfig(channel_name="Transcode Count",
                                             emoji=Emoji.Transcode,
                                             data=stats_types.get_subsection_data("TranscodeCount")).to_model()
        plex_availability = VoiceChannelConfig(channel_name="Plex Availability",
                                               emoji=Emoji.Status,
                                               data=stats_types.get_subsection_data(
                                                   "PlexServerAvailability")).to_model()

        return settings_models.ActivityStats(
            category_name=category_name,
            enable=enable,
            bandwidth=bandwidth,
            local_bandwidth=local_bandwidth,
            remote_bandwidth=remote_bandwidth,
            stream_count=stream_count,
            transcode_count=transcode_count,
            plex_availability=plex_availability
        )


class StatsLibrariesConfig(ConfigSection):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def to_model(self) -> settings_models.LibraryStats:
        category_name = self.get_value(key="CategoryName", default="Plex Libraries")
        enable = utils.extract_boolean(self.get_value(key="Enable", default=False))

        libraries = []
        libraries_data: list[dict] = self.get_value(key="Libraries", default=[])
        for library_details in libraries_data:
            details_config = ConfigSection(data=library_details)

            library_name = details_config.get_value(key="Name", default="")
            alternate_name = details_config.get_value(key="AlternateName", default="")
            voice_channel_name = alternate_name if alternate_name else library_name
            movie = VoiceChannelConfig(channel_name=voice_channel_name,
                                       emoji=Emoji.Movie,
                                       data=details_config.get_subsection_data("Movies")).to_model()
            album = VoiceChannelConfig(channel_name=voice_channel_name,
                                       emoji=Emoji.Album,
                                       data=details_config.get_subsection_data("Albums")).to_model()
            artist = VoiceChannelConfig(channel_name=voice_channel_name,
                                        emoji=Emoji.Artist,
                                        data=details_config.get_subsection_data("Artists")).to_model()
            episode = VoiceChannelConfig(channel_name=voice_channel_name,
                                         emoji=Emoji.Episode,
                                         data=details_config.get_subsection_data("Episodes")).to_model()
            series = VoiceChannelConfig(channel_name=voice_channel_name,
                                        emoji=Emoji.Series,
                                        data=details_config.get_subsection_data("Series")).to_model()
            track = VoiceChannelConfig(channel_name=voice_channel_name,
                                       emoji=Emoji.Track,
                                       data=details_config.get_subsection_data("Tracks")).to_model()

            libraries.append(
                settings_models.Library(
                    name=library_name,
                    alternate_name=alternate_name,
                    voice_channels=settings_models.LibraryVoiceChannels(
                        movie=movie,
                        album=album,
                        artist=artist,
                        episode=episode,
                        series=series,
                        track=track
                    )
                )
            )

        combined_libraries = []
        combined_libraries_data: list[dict] = self.get_value(key="CombinedLibraries", default=[])
        for combined_library_details in combined_libraries_data:
            details_config = ConfigSection(data=combined_library_details)

            combined_library_name = details_config.get_value(key="Name", default="")
            combined_library_names = details_config.get_value(key="Libraries", default=[])
            movie = VoiceChannelConfig(channel_name=combined_library_name,
                                       emoji=Emoji.Movie,
                                       data=details_config.get_subsection_data("Movies")).to_model()
            album = VoiceChannelConfig(channel_name=combined_library_name,
                                       emoji=Emoji.Album,
                                       data=details_config.get_subsection_data("Albums")).to_model()
            artist = VoiceChannelConfig(channel_name=combined_library_name,
                                        emoji=Emoji.Artist,
                                        data=details_config.get_subsection_data("Artists")).to_model()
            episode = VoiceChannelConfig(channel_name=combined_library_name,
                                         emoji=Emoji.Episode,
                                         data=details_config.get_subsection_data("Episodes")).to_model()
            series = VoiceChannelConfig(channel_name=combined_library_name,
                                        emoji=Emoji.Series,
                                        data=details_config.get_subsection_data("Series")).to_model()
            track = VoiceChannelConfig(channel_name=combined_library_name,
                                       emoji=Emoji.Track,
                                       data=details_config.get_subsection_data("Tracks")).to_model()

            combined_libraries.append(
                settings_models.CombinedLibrary(
                    name=combined_library_name,
                    libraries=combined_library_names,
                    voice_channels=settings_models.LibraryVoiceChannels(
                        movie=movie,
                        album=album,
                        artist=artist,
                        episode=episode,
                        series=series,
                        track=track
                    )
                )
            )

        refresh_interval_seconds = self.get_value(key="RefreshSeconds", default=15)

        return settings_models.LibraryStats(
            category_name=category_name,
            enable=enable,
            libraries=libraries,
            combined_libraries=combined_libraries,
            refresh_interval_seconds=refresh_interval_seconds
        )


class StatsPerformanceConfig(ConfigSection):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def to_model(self) -> settings_models.PerformanceStats:
        category_name = self.get_value(key="CategoryName", default="Performance")
        enable = utils.extract_boolean(self.get_value(key="Enable", default=False))

        metrics = ConfigSection(data=self.get_subsection_data(key="Metrics"))
        cpu = VoiceChannelConfig(channel_name="CPU",
                                 emoji=Emoji.CPU,
                                 data=metrics.get_subsection_data("CPU")).to_model()
        memory = VoiceChannelConfig(channel_name="Memory",
                                    emoji=Emoji.Memory,
                                    data=metrics.get_subsection_data("Memory")).to_model()
        disk = VoiceChannelConfig(channel_name="Disk",
                                  emoji=Emoji.Disk,
                                  data=metrics.get_subsection_data("DiskSpace")).to_model()
        user_count = VoiceChannelConfig(channel_name="User Count",
                                        emoji=Emoji.Person,
                                        data=metrics.get_subsection_data("UserCount")).to_model()

        return settings_models.PerformanceStats(
            category_name=category_name,
            enable=enable,
            cpu=cpu,
            memory=memory,
            disk=disk,
            user_count=user_count
        )


class StatsConfig(ConfigSection):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def to_model(self) -> settings_models.Stats:
        activity = StatsActivityConfig(data=self.get_subsection_data(key="Activity")).to_model()
        library = StatsLibrariesConfig(data=self.get_subsection_data(key="Libraries")).to_model()
        performance = StatsPerformanceConfig(data=self.get_subsection_data(key="Performance")).to_model()

        return settings_models.Stats(
            activity=activity,
            library=library,
            performance=performance
        )


class TautulliConfig(ConfigSection):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def to_model(self) -> settings_models.Tautulli:
        api_key = self.get_value(key="APIKey")
        url = self.get_value(key="URL")
        ignore_ssl = utils.extract_boolean(self.get_value(key="UseSelfSignedCert", default=False))
        refresh_interval_seconds = self.get_value(key='RefreshSeconds', default=15)
        termination_message = self.get_value(key='TerminateMessage', default="Your stream has ended.")

        return settings_models.Tautulli(
            api_key=api_key,
            url=url,
            ignore_ssl=ignore_ssl,
            refresh_interval_seconds=refresh_interval_seconds,
            termination_message=termination_message
        )


class RunArgsConfig(ConfigSection):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def to_model(self) -> settings_models.RunArgs:
        performance_disk_space_mapping = self.get_value(key=KEY_RUN_ARGS_MONITOR_PATH, default=None)
        config_path = self.get_value(key=KEY_RUN_ARGS_CONFIG_PATH, default=None)
        log_path = self.get_value(key=KEY_RUN_ARGS_LOG_PATH, default=None)

        return settings_models.RunArgs(
            performance_disk_space_mapping=performance_disk_space_mapping,
            config_path=config_path,
            log_path=log_path
        )


class Config:
    discord: settings_models.Discord
    display: settings_models.Display
    extras: settings_models.Extras
    stats: settings_models.Stats
    tautulli: settings_models.Tautulli
    run_args: settings_models.RunArgs

    def __init__(self, config_path: str, **docker_kwargs):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        logging.debug(f"Loaded config from {config_path}")
        self.yaml_data = yaml.load(open(config_path), Loader=yaml.FullLoader)
        self.json_data = json.loads(json.dumps(self.yaml_data, indent=4))

        start = ConfigSection(data=self.json_data)

        self.tautulli = TautulliConfig(data=start.get_subsection_data(key="Tautulli")).to_model()
        self.discord = DiscordConfig(data=start.get_subsection_data(key="Discord")).to_model()
        self.extras = ExtrasConfig(data=start.get_subsection_data(key="Extras")).to_model()
        self.display = DisplayConfig(data=start.get_subsection_data(key="Display")).to_model()
        self.stats = StatsConfig(data=start.get_subsection_data(key="Stats")).to_model()
        self.run_args = RunArgsConfig(data=docker_kwargs).to_model()

    def as_json(self) -> dict:
        return {
            "Tautulli": self.tautulli.as_dict(),
            "Discord": self.discord.as_dict(),
            "Extras": self.extras.as_dict(),
            "Display": self.display.as_dict(),
            "Stats": self.stats.as_dict(),
            "Run Args": self.run_args.as_dict()
        }

    def as_yaml(self) -> str:
        return yaml.dump(self.as_json(), default_flow_style=False, sort_keys=False)

    def __repr__(self) -> str:
        return self.as_yaml()

    def print(self) -> str:
        return self.as_yaml()
