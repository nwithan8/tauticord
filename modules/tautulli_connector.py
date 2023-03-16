from typing import List, Tuple, Union, Dict

import discord
import tautulli

import modules.logs as logging
import modules.statics as statics
from modules import utils, emojis
from modules.emojis import EmojiManager

session_ids = {}


class Session:
    def __init__(self, session_data, time_settings: dict):
        self._data = session_data
        self._time_settings = time_settings

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
        eta_datetime = utils.now_plus_milliseconds(milliseconds=milliseconds_remaining,
                                                   timezone_code=self._time_settings['timezone'])
        eta_string = utils.datetime_to_string(datetime_object=eta_datetime,
                                              template=("%H:%M" if self._time_settings['mil_time'] else "%I:%M %p"))
        return eta_string

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
        return emoji_manager.get_emoji(self._data.get('state', ""))

    def get_type_icon(self, emoji_manager: EmojiManager) -> str:
        key = self._data.get('media_type', "")
        if self._data.get('live'):
            key = 'live'
        emoji = emoji_manager.get_emoji(key)
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

    def get_session_title(self, session_number: int, emoji_manager: EmojiManager) -> str:
        emoji = emojis.emoji_from_stream_number(session_number)
        return statics.session_title_message.format(emoji=emoji,
                                                    icon=self.get_status_icon(emoji_manager=emoji_manager),
                                                    media_type_icon=self.get_type_icon(emoji_manager=emoji_manager),
                                                    title=self.title)

    def get_session_user(self, emoji_manager: EmojiManager) -> str:
        emoji = emoji_manager.get_emoji("person")
        return statics.session_user_message.format(emoji=emoji, username=self.username)

    def get_session_player(self, emoji_manager: EmojiManager) -> str:
        emoji = emoji_manager.get_emoji("device")
        return statics.session_player_message.format(emoji=emoji, product=self.product, player=self.player)

    def get_session_details(self, emoji_manager: EmojiManager) -> str:
        emoji = emoji_manager.get_emoji("resolution")
        return statics.session_details_message.format(emoji=emoji, quality_profile=self.quality_profile,
                                                      bandwidth=self.bandwidth,
                                                      transcoding=self.transcoding_stub)

    def get_session_progress(self, emoji_manager: EmojiManager) -> str:
        emoji = emoji_manager.get_emoji("progress")
        return statics.session_progress_message.format(emoji=emoji, progress=self.progress_marker, eta=self.eta)


class Activity:
    def __init__(self, activity_data, time_settings: dict, emoji_manager: EmojiManager):
        self._data = activity_data
        self._time_settings = time_settings
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

    def get_message(self) -> str:
        overview_message = ""
        if self.stream_count > 0:
            overview_message += statics.sessions_message.format(stream_count=self.stream_count,
                                                                word=utils.make_plural(word='stream',
                                                                                       count=self.stream_count))
            if self.transcode_count > 0:
                overview_message += f" ({statics.transcodes_message.format(transcode_count=self.transcode_count, word=utils.make_plural(word='transcode', count=self.transcode_count))})"

        if self.total_bandwidth:
            bandwidth_emoji = self._emoji_manager.get_emoji('bandwidth')
            overview_message += f" @ {statics.bandwidth_message.format(emoji=bandwidth_emoji, bandwidth=self.total_bandwidth)}"
            if self.lan_bandwidth:
                lan_bandwidth_emoji = self._emoji_manager.get_emoji('home')
                overview_message += f" {statics.lan_bandwidth_message.format(emoji=lan_bandwidth_emoji, bandwidth=self.lan_bandwidth)}"

        return overview_message

    @property
    def sessions(self) -> List[Session]:
        return [Session(session_data=session_data, time_settings=self._time_settings) for session_data in
                self._data.get('sessions', [])]


class TautulliStreamInfo:
    def __init__(self, session: Session, session_number: int):
        self._session = session
        self._session_number = session_number

    def get_title(self, emoji_manager: EmojiManager) -> str:
        try:
            return self._session.get_session_title(session_number=self._session_number, emoji_manager=emoji_manager)
        except Exception as title_exception:
            return "Unknown"

    def get_player(self, emoji_manager: EmojiManager) -> str:
        return self._session.get_session_player(emoji_manager=emoji_manager)

    def get_user(self, emoji_manager: EmojiManager) -> str:
        return self._session.get_session_user(emoji_manager=emoji_manager)

    def get_details(self, emoji_manager: EmojiManager) -> str:
        return self._session.get_session_details(emoji_manager=emoji_manager)

    def get_progress(self, emoji_manager: EmojiManager) -> str:
        return self._session.get_session_progress(emoji_manager=emoji_manager)

    def get_body(self, emoji_manager: EmojiManager) -> str:
        try:
            return f"{self.get_user(emoji_manager=emoji_manager)}\n{self.get_player(emoji_manager=emoji_manager)}\n{self.get_details(emoji_manager=emoji_manager)}\n{self.get_progress(emoji_manager=emoji_manager)}"
        except Exception as body_exception:
            logging.error(str(body_exception))
            return f"Could not display data for session {self._session_number}"


class TautulliDataResponse:
    def __init__(self,
                 overview_message: str,
                 server_name: str,
                 emoji_manager: EmojiManager,
                 streams_info: List[TautulliStreamInfo] = None,
                 plex_pass: bool = False,
                 error_occurred: bool = False):
        self._overview_message = overview_message
        self._streams = streams_info or []
        self.plex_pass = plex_pass
        self.error = error_occurred
        self._emoji_manager = emoji_manager
        self._server_name = server_name

    @property
    def embed(self) -> discord.Embed:
        if len(self._streams) <= 0:
            return discord.Embed(title="No current activity")
        embed = discord.Embed(title=f"Current activity on {self._server_name}")
        for stream in self._streams:
            embed.add_field(name=stream.get_title(emoji_manager=self._emoji_manager),
                            value=stream.get_body(emoji_manager=self._emoji_manager), inline=False)
        footer_text = self._overview_message
        if self.plex_pass:
            footer_text += f"\n\nTo terminate a stream, react with the stream number."
        embed.set_footer(text=footer_text)
        return embed


class TautulliConnector:
    def __init__(self,
                 base_url: str,
                 api_key: str,
                 terminate_message: str,
                 analytics,
                 plex_pass: bool,
                 time_settings: dict,
                 server_name: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.api = tautulli.RawAPI(base_url=base_url, api_key=api_key)
        self.server_name = server_name or self.api.server_friendly_name
        self.terminate_message = terminate_message
        self.analytics = analytics
        self.plex_pass = plex_pass
        self.time_settings = time_settings

    def _error_and_analytics(self, error_message, function_name) -> None:
        logging.error(error_message)
        self.analytics.event(event_category="Error", event_action=function_name, random_uuid_if_needed=True)

    def refresh_data(self, emoji_manager: EmojiManager) -> Tuple[
        TautulliDataResponse, int, Union[Activity, None], bool]:
        """
        Parse activity JSON from Tautulli, prepare summary message for Discord
        :return: data wrapper, number of active streams, activity data and whether Plex is online
        """
        global session_ids
        data = self.api.activity()
        if data:
            logging.debug(f"JSON returned by GET request: {data}")
            try:
                activity = Activity(activity_data=data, time_settings=self.time_settings, emoji_manager=emoji_manager)
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
                return TautulliDataResponse(overview_message=activity.get_message(),
                                            emoji_manager=emoji_manager,
                                            streams_info=session_details,
                                            plex_pass=self.plex_pass,
                                            server_name=self.server_name), count, activity, self.is_plex_server_online()
            except KeyError as e:
                self._error_and_analytics(error_message=e, function_name='refresh_data (KeyError)')
        return TautulliDataResponse(overview_message="**Connection lost.**", emoji_manager=emoji_manager,
                                    error_occurred=True,
                                    server_name=self.server_name), 0, None, False  # If Tautulli is offline, assume Plex is offline

    def stop_stream(self, emoji, stream_number) -> str:
        """
        Stop a Plex stream
        :param emoji: Emoji used to stop the stream
        :param stream_number: stream number used to react to Discord message (ex. 1, 2, 3)
        :return: Success/failure message
        """
        if stream_number not in session_ids.keys():
            return "**Invalid stream number.**"
        logging.info(f"User attempting to stop session {emoji}, id {session_ids[stream_number]}")
        try:
            if self.api.terminate_session(session_id=session_ids[stream_number], message=self.terminate_message):
                return f"Stream {emoji} was stopped."
            else:
                return f"Stream {emoji} could not be stopped."
        except Exception as e:
            self._error_and_analytics(error_message=e, function_name='stop_stream')
        return "Something went wrong."

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

    def get_library_item_count(self, library_name: str, emoji_manager: EmojiManager) -> List[Tuple[str, int]]:
        library_info = self.get_library_info(library_name=library_name)
        if not library_info:
            return [('', 0)]
        library_type = library_info.get('section_type')
        match library_type:
            case 'show':
                return [(emoji_manager.get_emoji("series"), library_info.get('count')), (emoji_manager.get_emoji("episodes"), library_info.get('child_count'))]
            case 'artist':
                return [(emoji_manager.get_emoji("artists"), library_info.get('count')), (emoji_manager.get_emoji("tracks"), library_info.get('child_count'))]
            case 'movie':
                return [(emoji_manager.get_emoji("movies"), library_info.get('count'))]
        return [(emoji_manager.get_emoji("unknown"), 0)]

    def is_plex_server_online(self) -> bool:
        return self.api.server_status.get("connected", False)
