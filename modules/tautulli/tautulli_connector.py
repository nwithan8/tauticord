from typing import List, Union, Optional

import objectrest
import tautulli

import modules.database.repository as db
import modules.logs as logging
import modules.settings.models as settings_models
from modules import utils
from modules.analytics import GoogleAnalytics
from modules.discord.models.tautulli_activity_summary import TautulliActivitySummary
from modules.discord.models.tautulli_recently_added_summary import TautulliRecentlyAddedSummary
from modules.discord.models.tautulli_stream_info import TautulliStreamInfo
from modules.emojis import EmojiManager
from modules.tautulli.enums import LibraryType, HomeStatType, StatMetricType, StatChartType
from modules.tautulli.models.activity import Activity
from modules.tautulli.models.library_item_counts import LibraryItemCounts
from modules.tautulli.models.recently_added_media_item import RecentlyAddedMediaItem
from modules.tautulli.models.stats import PlayCountStats, PlayDurationStats
from modules.utils import status_code_is_success


class TautulliConnector:
    def __init__(self,
                 tautulli_settings: settings_models.Tautulli,
                 display_settings: settings_models.Display,
                 stats_settings: settings_models.Stats,
                 database_path: str,
                 analytics: GoogleAnalytics):
        self.base_url = tautulli_settings.url
        self.api_key = tautulli_settings.api_key

        logging.info(f"Connecting to Tautulli at {self.base_url}...")
        try:
            # Disable SSL verification because of self-signed certs
            self.api = tautulli.RawAPI(base_url=self.base_url, api_key=self.api_key, verify=True,
                                       ssl_verify=not tautulli_settings.ignore_ssl)
        except Exception as e:
            # common issue - `base_url` is empty because config was not parsed properly,
            # causes "'NoneType' object has no attribute 'endswith'" error inside Tautulli API library
            raise Exception(
                f"Could not begin a Tautulli connection. Please check that your configuration is complete and "
                f"reachable. Exception: {e}") from e

        self.server_name = display_settings.plex_server_name or self.api.server_friendly_name
        self.terminate_message = tautulli_settings.termination_message
        self.analytics = analytics
        self.text_manager = display_settings.text_manager
        self.time_manager = display_settings.time.time_manager
        self.stats_settings = stats_settings
        self.database = db.DatabaseRepository(database_path=database_path)

        self.has_plex_pass = self.api.shortcuts.has_plex_pass
        self.plex_url = self.api.server_info.get('pms_url', None)

        self.plex_api = None
        try:
            self.plex_api = self.api.shortcuts.plex_api
        except Exception as e:  # Could not prepare Plex API
            logging.error(f"Could not prepare Plex API: {e}")

        tautulli_version = self.api.shortcuts.api_version
        logging.debug(f"Connected to Tautulli version: {tautulli_version}")

        self.session_id_mappings = {}

    def _error_and_analytics(self, error_message, function_name) -> None:
        logging.error(error_message)
        self.analytics.event(event_category="Error", event_action=function_name, random_uuid_if_needed=True)

    def plex_pass_feature_is_allowed(self, feature: bool, warning: Optional[str] = None) -> bool:
        if not self.has_plex_pass:
            if feature and warning:  # Only log warning if feature was attempted to be used
                logging.warning(warning)
            return False

        return feature

    def refresh_data(self,
                     enable_stream_termination_if_possible: bool,
                     emoji_manager: EmojiManager,
                     additional_embed_fields: List[dict] = None,
                     additional_embed_footers: List[str] = None) -> TautulliActivitySummary:
        """
        Parse activity JSON from Tautulli, prepare summary message for Discord
        :return: data wrapper with activity summary
        """
        # Erase session ID mappings from last refresh
        self.session_id_mappings = {}

        # Add termination tip if enabled
        if self.plex_pass_feature_is_allowed(feature=enable_stream_termination_if_possible):
            additional_embed_footers = additional_embed_footers or []
            additional_embed_footers.append(
                f"To terminate a stream, react with the stream number.")

        data = self.api.activity()

        # Tautulli returned data (is online)
        if data:
            logging.debug(f"JSON returned by GET request: {data}")

            activity = Activity(activity_data=data, time_manager=self.time_manager, emoji_manager=emoji_manager)

            # Store session IDs for stopping streams later
            session_details = []
            for session_number, session in enumerate(activity.sessions):
                session_details.append(TautulliStreamInfo(session=session,
                                                          session_number=session_number + 1))  # +1 for human-readable numbering
                self.session_id_mappings[session_number + 1] = str(session.id)

            return TautulliActivitySummary(activity=activity,
                                           plex_online=self.is_plex_server_online(),
                                           emoji_manager=emoji_manager,
                                           text_manager=self.text_manager,
                                           streams=session_details,
                                           server_name=self.server_name,
                                           additional_embed_fields=additional_embed_fields,
                                           additional_embed_footers=additional_embed_footers)

        # Tautulli did not return data (is offline)
        is_plex_online = self.ping_pms_server_directly()  # Check directly if Plex is online
        return TautulliActivitySummary(activity=None,
                                       plex_online=is_plex_online,
                                       emoji_manager=emoji_manager,
                                       text_manager=self.text_manager,
                                       error_occurred=True,
                                       server_name=self.server_name,
                                       additional_embed_fields=additional_embed_fields,
                                       additional_embed_footers=additional_embed_footers)

    def ping_pms_server_directly(self) -> bool:
        """
        Ping Plex Media Server directly
        :return: True if successfully reached, False otherwise
        :rtype: bool
        """
        if not self.plex_url:
            logging.error("Could not ping Plex Media Server directly: Plex details not found")
            return False

        try:
            status_code = objectrest.get(url=self.plex_url, verify=False).status_code
            return status_code_is_success(
                status_code=status_code) or status_code == 401  # 401 is a success because it means we got a response
        except Exception as e:
            logging.error(f"Could not ping Plex Media Server directly: {e}")
            return False

    def stop_stream(self, emoji, stream_number: int) -> str:
        """
        Stop a Plex stream
        :param emoji: Emoji used to stop the stream
        :param stream_number: stream number used to react to Discord message (ex. 1, 2, 3)
        :return: Success/failure message
        """
        if stream_number not in self.session_id_mappings.keys():
            return utils.bold(
                f"Invalid stream number: {stream_number}. Valid stream numbers: {', '.join([str(x) for x in self.session_id_mappings.keys()])}")

        session_id = self.session_id_mappings[stream_number]

        logging.info(f"User attempting to stop session {emoji}, id {session_id}")

        try:
            if self.api.terminate_session(session_id=session_id, message=self.terminate_message):
                return f"Stream {emoji} was stopped."
            else:
                return f"Stream {emoji} could not be stopped."
        except Exception as e:
            self._error_and_analytics(error_message=e, function_name='stop_stream')

        return "Something went wrong."

    def get_user_count(self) -> int:
        """
        Get the number of users with access to the Plex server
        :return: Number of users
        """
        users = self.api.users
        if not users:
            return 0
        active_users = [user for user in users if user.get('is_active', False)]
        return len(active_users)

    def get_library_id(self, library_name: str) -> Union[str, None]:
        library_name = library_name.strip()
        for library in self.api.library_names:
            if library.get('section_name').strip() == library_name:
                return library.get('section_id')
        logging.error(f"Could not get ID for library {library_name}")
        return None

    def get_library_info(self, library_name: str, library_id: int = None) -> Union[dict, None]:
        logging.info(f"Collecting stats about library \"{library_name}\"")

        # Use library ID if provided, otherwise get it from the name

        if not library_id:
            library_id = self.get_library_id(library_name=library_name)

        if not library_id:
            return None

        return self.api.get_library(section_id=library_id)

    def get_item_counts_for_a_single_library(self,
                                             library_name: str,
                                             library_id: int = None) -> LibraryItemCounts | None:
        library_info = self.get_library_info(library_name=library_name, library_id=library_id)
        logging.debug(f"JSON returned by GET request: {library_info}")

        if not library_info:
            return None

        library_type: LibraryType = LibraryType.from_str(value=library_info.get('section_type'))

        movies = 0
        series = 0
        episodes = 0
        artists = 0
        albums = 0
        tracks = 0

        match library_type:
            case LibraryType.MOVIE:
                movies = library_info.get('count')
            case LibraryType.SHOW:
                series = library_info.get('count')
                episodes = library_info.get('child_count')
            case LibraryType.MUSIC:
                artists = library_info.get('count')
                albums = library_info.get('parent_count')
                tracks = library_info.get('child_count')

        return LibraryItemCounts(
            library_name=library_name,
            library_type=library_type,
            movies=movies,
            series=series,
            episodes=episodes,
            artists=artists,
            albums=albums,
            tracks=tracks
        )

    def get_item_counts_for_multiple_combined_libraries(self,
                                                        combined_library_name: str,
                                                        sub_libraries: List[
                                                            settings_models.CombinedLibrarySubLibrary]) -> LibraryItemCounts | None:
        rolling_library_type = None

        movies = 0
        series = 0
        episodes = 0
        artists = 0
        albums = 0
        tracks = 0

        for library in sub_libraries:
            library_item_counts = self.get_item_counts_for_a_single_library(library_name=library.name,
                                                                            library_id=library.library_id)

            if not library_item_counts:
                continue

            if rolling_library_type and rolling_library_type != library_item_counts.library_type:
                logging.error(
                    f"Library types do not match: {library.name} ({library_item_counts.library_type}) and {combined_library_name} ({rolling_library_type}). Cannot combine stats for different types of libraries.")
                return None

            rolling_library_type = library_item_counts.library_type

            movies += library_item_counts.movies
            series += library_item_counts.series
            episodes += library_item_counts.episodes
            artists += library_item_counts.artists
            albums += library_item_counts.albums
            tracks += library_item_counts.tracks

        return LibraryItemCounts(
            library_name=combined_library_name,
            library_type=rolling_library_type,
            movies=movies,
            series=series,
            episodes=episodes,
            artists=artists,
            albums=albums,
            tracks=tracks
        )

    def get_recently_added_count_for_library(self, library_name: str, minutes: int) -> int | None:
        results = self.database.get_all_recently_added_items_in_past_x_minutes_for_libraries(minutes=minutes,
                                                                                        library_names=[library_name])
        return len(results)

    def get_recently_added_count_for_combined_libraries(self,
                                                        sub_libraries: List[
                                                            settings_models.CombinedLibrarySubLibrary],
                                                        minutes: int) -> int | None:
        library_names = [library.name for library in sub_libraries]
        results = self.database.get_all_recently_added_items_in_past_x_minutes_for_libraries(minutes=minutes,
                                                                                        library_names=library_names)

        return len(results)

    def is_plex_server_online(self) -> bool:
        return self.api.server_status.get("connected", False)

    def get_user_id_by_username(self, username: str) -> Union[str, None]:
        for user in self.api.users:
            if user.get('username') == username:
                return user.get('user_id')
        return None

    def get_stats_for_x_days(self, stat_type: HomeStatType, metric: str, days: int, limit: int) -> List[dict]:
        stats = self.api.get_home_stats(
            stats_type=metric,
            time_range=days,
            count=limit,
            stat_id=stat_type.value,
        )

        if not stats:
            return []

        old_data = stats.get('rows', [])
        new_data = []
        for item in old_data:
            copy = item
            copy['total'] = item.get('total_plays' if metric == StatMetricType.PLAYS.value else 'total_duration', 0)
            new_data.append(copy)

        # noinspection PyUnresolvedReferences
        return new_data

    def get_play_count_chart_data(self, chart_type: StatChartType, days: int,
                                  user_ids: List[str] = None) -> PlayCountStats | None:
        data = None

        match chart_type:
            case StatChartType.DAILY_BY_MEDIA_TYPE:
                data = self.api.get_plays_by_date(time_range=days, y_axis=StatMetricType.PLAYS.value, user_ids=user_ids)
            case StatChartType.BY_HOUR_OF_DAY:
                data = self.api.get_plays_by_hour_of_day(time_range=days, y_axis=StatMetricType.PLAYS.value,
                                                         user_ids=user_ids)
            case StatChartType.BY_DAY_OF_WEEK:
                data = self.api.get_plays_by_day_of_week(time_range=days, y_axis=StatMetricType.PLAYS.value,
                                                         user_ids=user_ids)
            case StatChartType.BY_TOP_10_PLATFORMS:
                data = self.api.get_plays_by_top_10_platforms(time_range=days, y_axis=StatMetricType.PLAYS.value,
                                                              user_ids=user_ids)
            case StatChartType.BY_TOP_10_USERS:
                data = self.api.get_plays_by_top_10_users(time_range=days, y_axis=StatMetricType.PLAYS.value,
                                                          user_ids=user_ids)

        if not data:
            return None

        return PlayCountStats(data=data)

    def get_play_duration_chart_data(self, chart_type: StatChartType, days: int,
                                     user_ids: List[str] = None) -> PlayDurationStats | None:
        data = None

        match chart_type:
            case StatChartType.DAILY_BY_MEDIA_TYPE:
                data = self.api.get_plays_by_date(time_range=days, y_axis=StatMetricType.DURATION.value,
                                                  user_ids=user_ids)
            case StatChartType.BY_HOUR_OF_DAY:
                data = self.api.get_plays_by_hour_of_day(time_range=days, y_axis=StatMetricType.DURATION.value,
                                                         user_ids=user_ids)
            case StatChartType.BY_DAY_OF_WEEK:
                data = self.api.get_plays_by_day_of_week(time_range=days, y_axis=StatMetricType.DURATION.value,
                                                         user_ids=user_ids)
            case StatChartType.BY_TOP_10_PLATFORMS:
                data = self.api.get_plays_by_top_10_platforms(time_range=days, y_axis=StatMetricType.DURATION.value,
                                                              user_ids=user_ids)
            case StatChartType.BY_TOP_10_USERS:
                data = self.api.get_plays_by_top_10_users(time_range=days, y_axis=StatMetricType.DURATION.value,
                                                          user_ids=user_ids)

        if not data:
            return None

        return PlayDurationStats(data=data)

    def get_recently_added_media(self, count: int, media_type: Optional[str] = None) -> list[RecentlyAddedMediaItem]:
        data = self.api.get_recently_added(count=count, media_type=media_type)
        recently_added = data.get('recently_added', [])

        items = []
        for element in recently_added:
            item = RecentlyAddedMediaItem()

            # Movies only have one title
            title = element.get('title', '')
            # Shows have SHOW - SEASON - EPISODE titles
            if parent_title := element.get('parent_title', ''):
                title = f"{parent_title} - {title}"
            if grandparent_title := element.get('grandparent_title', ''):
                title = f"{grandparent_title} - {title}"
            item.title = title

            partial_poster_url = element.get('thumb', '')
            full_poster_url = self.api.shortcuts.get_plex_image_url_from_proxy(plex_image_path=partial_poster_url)
            item.poster_url = full_poster_url

            item.summary = element.get('summary', '')

            item.library = element.get('library_name', '')

            rating_key = element.get('rating_key', '')
            item.link = self.api.shortcuts.get_link_to_open_media_item_in_browser(media_item_id=rating_key)

            items.append(item)

        return items

    def get_recently_added_media_summary(self, count: int, media_type: Optional[str] = None, footer: str = None) \
            -> TautulliRecentlyAddedSummary:
        items: list[RecentlyAddedMediaItem] = self.get_recently_added_media(count=count, media_type=media_type)

        return TautulliRecentlyAddedSummary(items=items, footer=footer)
