import discord

import modules.logs as logging
import modules.settings.models
from modules.tasks.voice_category_stats import VoiceCategoryStatsMonitor
from modules.tautulli.models.library_item_counts import LibraryItemCounts
from modules.tautulli.tautulli_connector import TautulliConnector


class LibraryStats(VoiceCategoryStatsMonitor):
    def __init__(self,
                 discord_client,
                 settings: modules.settings.models.LibraryStats,
                 tautulli_connector: TautulliConnector,
                 guild_id: int,
                 voice_category: discord.CategoryChannel = None):
        super().__init__(discord_client=discord_client,
                         guild_id=guild_id,
                         service_entrypoint=self.update_library_stats,
                         voice_category=voice_category)
        self.stats_settings = settings
        self.tautulli = tautulli_connector

    async def update_library_stats_for_library(self,
                                               library_settings: modules.settings.models.BaseLibrary,
                                               item_counts: LibraryItemCounts) -> None:
        """
        Update the individual stat voice channels for a single library/combined library
        (e.g. "My Library" - Movies, Shows, Episodes, Artists, Albums, Tracks)
        """
        if not item_counts:
            return

        match item_counts.library_type:
            case modules.tautulli.tautulli_connector.LibraryType.MOVIE:
                if library_settings.voice_channels.movie.enable:
                    await self.edit_stat_voice_channel(voice_channel_settings=library_settings.voice_channels.movie,
                                                       stat=item_counts.movies)
            case modules.tautulli.tautulli_connector.LibraryType.SHOW:
                if library_settings.voice_channels.series.enable:
                    await self.edit_stat_voice_channel(voice_channel_settings=library_settings.voice_channels.series,
                                                       stat=item_counts.series)
                if library_settings.voice_channels.episode.enable:
                    await self.edit_stat_voice_channel(voice_channel_settings=library_settings.voice_channels.episode,
                                                       stat=item_counts.episodes)
            case modules.tautulli.tautulli_connector.LibraryType.MUSIC:
                if library_settings.voice_channels.artist.enable:
                    await self.edit_stat_voice_channel(voice_channel_settings=library_settings.voice_channels.artist,
                                                       stat=item_counts.artists)
                if library_settings.voice_channels.album.enable:
                    await self.edit_stat_voice_channel(voice_channel_settings=library_settings.voice_channels.album,
                                                       stat=item_counts.albums)
                if library_settings.voice_channels.track.enable:
                    await self.edit_stat_voice_channel(voice_channel_settings=library_settings.voice_channels.track,
                                                       stat=item_counts.tracks)

    async def update_library_stats(self) -> None:
        logging.info("Updating library stats...")

        # Only got here because library stats are enabled, no need to check

        """
        Update the individual stat voice channels for each regular library and each combined library
        """
        logging.info("Updating library stats...")

        # Only got here because library stats are enabled, no need to check

        # Regular libraries
        for library_settings in self.stats_settings.libraries:
            library_name = library_settings.name

            item_counts: modules.tautulli.tautulli_connector.LibraryItemCounts = (
                self.tautulli.get_item_counts_for_a_single_library(
                    library_name=library_name))

            await self.update_library_stats_for_library(library_settings=library_settings, item_counts=item_counts)

        # Combined libraries
        for library_settings in self.stats_settings.combined_libraries:
            library_name = library_settings.name

            item_counts: modules.tautulli.tautulli_connector.LibraryItemCounts = (
                self.tautulli.get_item_counts_for_multiple_combined_libraries(
                    combined_library_name=library_name, sub_library_names=library_settings.libraries))

            await self.update_library_stats_for_library(library_settings=library_settings, item_counts=item_counts)
