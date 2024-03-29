import enum
from typing import List, Tuple, Union, Optional

import discord
import objectrest
import tautulli

import modules.logs as logging
import modules.settings.models as settings_models
from modules import utils
from modules.analytics import GoogleAnalytics
from modules.emojis import EmojiManager
from modules.text_manager import TextManager
from modules.time_manager import TimeManager
from modules.utils import status_code_is_success, url_encode

session_ids = {}


class HomeStatMetricType(enum.Enum):
    PLAYS = 'plays'
    DURATION = 'duration'


class HomeStatType(enum.Enum):
    TOP_MOVIES = 'top_movies'
    POPULAR_MOVIES = 'popular_movies'
    TOP_TV = 'top_tv'
    POPULAR_TV = 'popular_tv'
    TOP_MUSIC = 'top_music'
    POPULAR_MUSIC = 'popular_music'
    TOP_LIBRARIES = 'top_libraries'
    TOP_USERS = 'top_users'
    TOP_PLATFORMS = 'top_platforms'
    LAST_WATCHED = 'last_watched'
    MOST_CONCURRENT = 'most_concurrent'


class RecentlyAddedMediaItem:
    title: str
    poster_url: str
    summary: str
    library: str
    link: str


class Session:
    def __init__(self, session_data, time_manager: TimeManager):
        self._data = session_data
        self._time_manager = time_manager

    @property
    def duration_milliseconds(self) -> int:
        value = self._data.get('duration', 0)
        try:
            value = int(value)
        except:
            value = 0
        return int(value)

    @property
    def location_milliseconds(self) -> int:
        value = self._data.get('view_offset', 0)
        try:
            value = int(value)
        except:
            value = 0
        return int(value)

    @property
    def progress_percentage(self) -> int:
        if not self.duration_milliseconds:
            return 0
        return int(self.location_milliseconds / self.duration_milliseconds)

    @property
    def progress_marker(self) -> str:
        current_progress_min_sec = utils.milliseconds_to_minutes_seconds(milliseconds=self.location_milliseconds)
        total_min_sec = utils.milliseconds_to_minutes_seconds(milliseconds=self.duration_milliseconds)
        return f"{current_progress_min_sec}/{total_min_sec}"

    @property
    def eta(self) -> str:
        if not self.duration_milliseconds or not self.location_milliseconds:
            return "Unknown"
        milliseconds_remaining = self.duration_milliseconds - self.location_milliseconds
        return self._time_manager.now_plus_milliseconds_string(milliseconds=milliseconds_remaining)

    @property
    def title(self) -> str:
        if self._data.get('live'):
            return f"{self._data.get('grandparent_title', '')} - {self._data['title']}"
        elif self._data['media_type'] == 'episode':
            return f"{self._data.get('grandparent_title', '')} - S{self._data.get('parent_title', '').replace('Season ', '').zfill(2)}E{self._data.get('media_index', '').zfill(2)} - {self._data['title']}"
        else:
            return self._data.get('full_title')

    def get_status_icon(self, emoji_manager: EmojiManager) -> str:
        """
        Get icon for a stream state
        :return: emoji icon
        """
        return emoji_manager.get_emoji(key=self._data.get('state', ""))

    def get_type_icon(self, emoji_manager: EmojiManager) -> str:
        key = self._data.get('media_type', "")
        if self._data.get('live'):
            key = 'live'
        emoji = emoji_manager.get_emoji(key=key)
        if not emoji:
            logging.info(
                "New media_type to pick icon for: {}: {}".format(self._data['title'], self._data['media_type']))
            return '🎁'
        return emoji

    @property
    def id(self) -> str:
        return self._data['session_id']

    @property
    def username(self) -> str:
        return self._data['username']

    @property
    def friendly_name(self) -> str:
        return self._data['friendly_name']

    @property
    def product(self) -> str:
        return self._data['product']

    @property
    def player(self) -> str:
        return self._data['player']

    @property
    def quality_profile(self) -> str:
        return self._data['quality_profile']

    @property
    def bandwidth(self) -> str:
        value = self._data.get('bandwidth', 0)
        try:
            value = int(value)
        except:
            value = 0
        return utils.human_bitrate(float(value) * 1024)

    @property
    def is_transcoding(self) -> bool:
        return self.stream_container_decision == 'transcode'

    @property
    def transcoding_stub(self) -> str:
        return ' (Transcode)' if self.is_transcoding else ''

    @property
    def stream_container_decision(self) -> str:
        return self._data['stream_container_decision']


class Activity:
    def __init__(self, activity_data, time_manager: TimeManager, emoji_manager: EmojiManager):
        self._data = activity_data
        self._time_manager = time_manager
        self._emoji_manager = emoji_manager

    @property
    def stream_count(self) -> int:
        value = self._data.get('stream_count', 0)
        try:
            return int(value)
        except:
            return 0

    @property
    def transcode_count(self) -> int:
        # TODO: Tautulli is reporting the wrong data:
        # https://github.com/Tautulli/Tautulli/blob/444b138e97a272e110fcb4364e8864348eee71c3/plexpy/webserve.py#L6000
        # Judgment there made by transcode_decision
        # We want to consider stream_container_decision
        return max([0, [s.is_transcoding for s in self.sessions].count(True)])

    @property
    def total_bandwidth(self) -> Union[str, None]:
        value = self._data.get('total_bandwidth', 0)
        try:
            return utils.human_bitrate(float(value) * 1024)
        except:
            return None

    @property
    def lan_bandwidth(self) -> Union[str, None]:
        value = self._data.get('lan_bandwidth', 0)
        try:
            return utils.human_bitrate(float(value) * 1024)
        except:
            return None

    @property
    def wan_bandwidth(self) -> Union[str, None]:
        total = self._data.get('total_bandwidth', 0)
        lan = self._data.get('lan_bandwidth', 0)
        value = total - lan
        try:
            return utils.human_bitrate(float(value) * 1024)
        except:
            return None

    @property
    def sessions(self) -> List[Session]:
        return [Session(session_data=session_data, time_manager=self._time_manager) for session_data in
                self._data.get('sessions', [])]


class TautulliStreamInfo:
    def __init__(self, session: Session, session_number: int):
        self._session = session
        self._session_number = session_number

    def get_title(self, emoji_manager: EmojiManager, text_manager: TextManager) -> str:
        try:
            return text_manager.session_title(session=self._session, session_number=self._session_number,
                                              emoji_manager=emoji_manager)
        except Exception as title_exception:
            return "Unknown"

    def get_body(self, emoji_manager: EmojiManager, text_manager: TextManager) -> str:
        try:
            return text_manager.session_body(session=self._session, emoji_manager=emoji_manager)
        except Exception as body_exception:
            logging.error(str(body_exception))
            return f"Could not display data for session {self._session_number}"


class TautulliDataResponse:
    def __init__(self,
                 activity: Union[Activity, None],
                 server_name: str,
                 emoji_manager: EmojiManager,
                 text_manager: TextManager,
                 streams_info: List[TautulliStreamInfo] = None,
                 plex_pass: bool = False,
                 error_occurred: bool = False,
                 additional_embed_fields: List[dict] = None,
                 additional_embed_footers: List[str] = None):
        self._activity = activity
        self._streams = streams_info or []
        self.plex_pass = plex_pass
        self.error = error_occurred
        self._emoji_manager = emoji_manager
        self._server_name = server_name
        self._text_manager = text_manager
        self.additional_embed_fields = additional_embed_fields or []
        self._additional_embed_footers = additional_embed_footers or []

    @property
    def embed(self) -> discord.Embed:
        title = f"Current activity on {self._server_name}"
        if len(self._streams) <= 0:
            title = "No current activity"

        embed = discord.Embed(title=title)

        for stream in self._streams:
            embed.add_field(name=stream.get_title(emoji_manager=self._emoji_manager, text_manager=self._text_manager),
                            value=stream.get_body(emoji_manager=self._emoji_manager, text_manager=self._text_manager),
                            inline=False)
        for field in self.additional_embed_fields:
            embed.add_field(name=field['name'], value=field['value'], inline=False)

        footer_text = self._text_manager.overview_footer(no_connection=self.error,
                                                         activity=self._activity,
                                                         emoji_manager=self._emoji_manager,
                                                         add_termination_tip=self.plex_pass)
        if self._additional_embed_footers:
            footer_text += "\n"
        for additional_footer in self._additional_embed_footers:
            footer_text += "\n" + additional_footer

        embed.set_footer(text=footer_text)

        return embed


class TautulliConnector:
    def __init__(self,
                 tautulli_settings: settings_models.Tautulli,
                 display_settings: settings_models.Display,
                 analytics: GoogleAnalytics):
        self.base_url = tautulli_settings.url
        self.api_key = tautulli_settings.api_key

        logging.info(f"Connecting to Tautulli at {self.base_url}...")
        try:
            # Disable SSL verification because of self-signed certs
            self.api = tautulli.RawAPI(base_url=self.base_url, api_key=self.api_key, verify=True,
                                       ssl_verify=not tautulli_settings.ignore_ssl)
        except Exception as e:
            # common issue - `base_url` is empty because config was not parsed properly, causes "'NoneType' object has no attribute 'endswith'" error inside Tautulli API library
            raise Exception(
                f"Could not begin a Tautulli connection. Please check that your configuration is complete and "
                f"reachable. Exception: {e}")

        self.server_name = display_settings.plex_server_name or self.api.server_friendly_name
        self.terminate_message = tautulli_settings.termination_message
        self.analytics = analytics
        self.text_manager = display_settings.text_manager
        self.time_manager = display_settings.time.time_manager

        self.plex_details = self.api.server_info
        self.plex_pass = False if not self.plex_details else self.plex_details.get('pms_plexpass', 0) == 1

        tautulli_version = self.api.shortcuts.api_version
        logging.debug(f"Connected to Tautulli version: {tautulli_version}")

    def _error_and_analytics(self, error_message, function_name) -> None:
        logging.error(error_message)
        self.analytics.event(event_category="Error", event_action=function_name, random_uuid_if_needed=True)

    def refresh_data(self, emoji_manager: EmojiManager, additional_embed_fields: List[dict] = None,
                     additional_embed_footers: List[str] = None) -> Tuple[
        TautulliDataResponse, int, Union[Activity, None], bool]:
        """
        Parse activity JSON from Tautulli, prepare summary message for Discord
        :return: data wrapper, number of active streams, activity data and whether Plex is online
        """
        global session_ids
        data = self.api.activity()

        # Tautulli returned data (is online)
        if data:
            logging.debug(f"JSON returned by GET request: {data}")
            try:
                activity = Activity(activity_data=data, time_manager=self.time_manager, emoji_manager=emoji_manager)
                sessions = activity.sessions
                count = 0
                session_ids = {}
                session_details = []
                for session in sessions:
                    try:
                        count += 1
                        session_details.append(TautulliStreamInfo(session=session, session_number=count))
                        session_ids[count] = str(session.id)
                    except ValueError as err:
                        self._error_and_analytics(error_message=err, function_name='refresh_data (ValueError)')
                        pass
                logging.debug(f"Count: {count}")
                return TautulliDataResponse(activity=activity,
                                            emoji_manager=emoji_manager,
                                            text_manager=self.text_manager,
                                            streams_info=session_details,
                                            plex_pass=self.plex_pass,
                                            server_name=self.server_name,
                                            additional_embed_fields=additional_embed_fields,
                                            additional_embed_footers=additional_embed_footers), count, activity, self.is_plex_server_online()
            except KeyError as e:
                self._error_and_analytics(error_message=e, function_name='refresh_data (KeyError)')

        # Tautulli did not return data (is offline)
        is_plex_online = self.ping_pms_server_directly()  # Check directly if Plex is online
        return TautulliDataResponse(activity=None,
                                    emoji_manager=emoji_manager,
                                    text_manager=self.text_manager,
                                    error_occurred=True,
                                    server_name=self.server_name,
                                    additional_embed_fields=additional_embed_fields,
                                    additional_embed_footers=additional_embed_footers), 0, None, is_plex_online

    def ping_pms_server_directly(self) -> bool:
        """
        Ping Plex Media Server directly
        :return: True if successfully reached, False otherwise
        :rtype: bool
        """
        if not self.plex_details:
            logging.error("Could not ping Plex Media Server directly: Plex details not found")
            return False

        try:
            pms_url = self.plex_details.get('pms_url')
            if not pms_url:
                return False
            status_code = objectrest.get(url=pms_url, verify=False).status_code
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
        if stream_number not in session_ids.keys():
            return utils.bold(
                f"Invalid stream number: {stream_number}. Valid stream numbers: {', '.join([str(x) for x in session_ids.keys()])}")
        logging.info(f"User attempting to stop session {emoji}, id {session_ids[stream_number]}")
        try:
            if self.api.terminate_session(session_id=session_ids[stream_number], message=self.terminate_message):
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

    def get_library_info(self, library_name: str) -> Union[dict, None]:
        logging.info(f"Collecting stats about library \"{library_name}\"")
        library_id = self.get_library_id(library_name=library_name)
        if not library_id:
            return None
        return self.api.get_library(section_id=library_id)

    def get_library_item_count(self, library_name: str, emoji_manager: EmojiManager,
                               visibility_settings: LibraryVoiceChannelsVisibilities) -> List[Tuple[str, int]]:
        library_info = self.get_library_info(library_name=library_name)
        logging.debug(f"JSON returned by GET request: {library_info}")
        if not library_info:
            return [('', 0)]
        library_type = library_info.get('section_type')
        results = []
        match library_type:
            case 'show':
                if visibility_settings.show_tv_series:
                    results.append((emoji_manager.get_emoji(key="series"), library_info.get('count')))
                if visibility_settings.show_tv_episodes:
                    results.append((emoji_manager.get_emoji(key="episodes"), library_info.get('child_count')))
                return results
            case 'artist':
                if visibility_settings.show_music_artists:
                    results.append((emoji_manager.get_emoji(key="artists"), library_info.get('count')))
                if visibility_settings.show_music_albums:
                    results.append((emoji_manager.get_emoji(key="albums"), library_info.get('parent_count')))
                if visibility_settings.show_music_tracks:
                    results.append((emoji_manager.get_emoji(key="tracks"), library_info.get('child_count')))
                return results
            case 'movie':
                return [(emoji_manager.get_emoji(key="movies"), library_info.get('count'))]
        return [(emoji_manager.get_emoji(key="unknown"), 0)]

    def get_combined_library_item_count(self, library_names: List[str], emoji_manager: EmojiManager,
                                        visibility_settings: LibraryVoiceChannelsVisibilities) -> List[Tuple[str, int]]:
        previous_library_name = None
        running_library_type = None
        running_total = 0
        emoji = emoji_manager.get_emoji(key="unknown")
        for library_name in library_names:
            library_info = self.get_library_info(library_name=library_name)

            if not library_info:
                continue

            library_type = library_info.get('section_type')
            if running_library_type and running_library_type != library_type:
                logging.error(
                    f"Library types do not match: {library_name} ({library_type}) and {previous_library_name} ({running_library_type}). Cannot combine stats for different types of libraries.")
                return []
            running_library_type = library_type
            previous_library_name = library_name

            match library_type:
                case 'show':
                    # Use the lowest child count possible
                    if visibility_settings.show_tv_episodes:
                        running_total += library_info.get('child_count')
                        emoji = emoji_manager.get_emoji(key="episodes")
                    else:
                        running_total += library_info.get('count')
                        emoji = emoji_manager.get_emoji(key="series")
                case 'artist':
                    # Use the lowest child count possible
                    if visibility_settings.show_music_tracks:
                        running_total += library_info.get('child_count')
                        emoji = emoji_manager.get_emoji(key="tracks")
                    else:
                        running_total += library_info.get('count')
                        emoji = emoji_manager.get_emoji(key="artists")
                case 'movie':
                    running_total += library_info.get('count')
                    emoji = emoji_manager.get_emoji(key="movies")

        return [(emoji, running_total)]

    def is_plex_server_online(self) -> bool:
        return self.api.server_status.get("connected", False)

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
            copy['total'] = item.get('total_plays' if metric == HomeStatMetricType.PLAYS.value else 'total_duration', 0)
            new_data.append(copy)

        # noinspection PyUnresolvedReferences
        return new_data

    def get_recently_added_media(self, count: int, media_type: Optional[str] = None) -> list[RecentlyAddedMediaItem]:
        data = self.api.get_recently_added(count=count, media_type=media_type)
        recently_added = data.get('recently_added', [])

        plex_server_details = self.plex_details
        pms_url = plex_server_details.get('pms_url')
        pms_id = plex_server_details.get('pms_identifier')

        def get_link_to_media_on_plex(rating_key: str) -> Union[str, None]:
            if not pms_url or not pms_id:
                return None

            media_id = f"/library/metadata/{rating_key}"
            return f"{pms_url}#!/server/{pms_id}/details?key={url_encode(media_id)}"

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
            item.link = get_link_to_media_on_plex(rating_key)

            items.append(item)

        return items
