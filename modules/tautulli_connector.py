from typing import List, Tuple, Union

import discord
import tautulli

import modules.statics as statics
from modules import utils
from modules.logs import *

session_ids = {}


class Activity:
    def __init__(self, activity_data, time_settings: dict):
        self._data = activity_data
        self._time_settings = time_settings

    @property
    def stream_count(self):
        value = self._data.get('stream_count', 0)
        try:
            return int(value)
        except:
            return 0

    @property
    def transcode_count(self):
        value = self._data.get('stream_count_transcode', 0)
        try:
            return int(value)
        except:
            return 0

    @property
    def total_bandwidth(self):
        value = self._data.get('total_bandwidth', 0)
        try:
            return utils.human_bitrate(float(value) * 1024)
        except:
            return None

    @property
    def lan_bandwidth(self):
        value = self._data.get('lan_bandwidth', 0)
        try:
            return utils.human_bitrate(float(value) * 1024)
        except:
            return None

    @property
    def wan_bandwidth(self):
        total = self._data.get('total_bandwidth', 0)
        lan = self._data.get('lan_bandwidth', 0)
        value = total - lan
        try:
            return utils.human_bitrate(float(value) * 1024)
        except:
            return None



    @property
    def message(self):
        overview_message = ""
        if self.stream_count > 0:
            overview_message += statics.sessions_message.format(stream_count=self.stream_count,
                                                                word=utils.make_plural(word='stream',
                                                                                       count=self.stream_count))
            if self.transcode_count > 0:
                overview_message += f" ({statics.transcodes_message.format(transcode_count=self.transcode_count, word=utils.make_plural(word='transcode', count=self.transcode_count))})"

        if self.total_bandwidth:
            overview_message += f" | {statics.bandwidth_message.format(bandwidth=self.total_bandwidth)}"
            if self.lan_bandwidth:
                overview_message += f" {statics.lan_bandwidth_message.format(bandwidth=self.lan_bandwidth)}"

        return overview_message

    @property
    def sessions(self):
        return [Session(session_data=session_data, time_settings=self._time_settings) for session_data in
                self._data.get('sessions', [])]


class Session:
    def __init__(self, session_data, time_settings: dict):
        self._data = session_data
        self._time_settings = time_settings

    @property
    def duration_milliseconds(self):
        value = self._data.get('duration', 0)
        try:
            value = int(value)
        except:
            value = 0
        return int(value)

    @property
    def location_milliseconds(self):
        value = self._data.get('view_offset', 0)
        try:
            value = int(value)
        except:
            value = 0
        return int(value)

    @property
    def progress_percentage(self):
        if not self.duration_milliseconds:
            return 0
        return int(self.location_milliseconds / self.duration_milliseconds)

    @property
    def progress_marker(self):
        current_progress_min_sec = utils.milliseconds_to_minutes_seconds(milliseconds=self.location_milliseconds)
        total_min_sec = utils.milliseconds_to_minutes_seconds(milliseconds=self.duration_milliseconds)
        return f"{current_progress_min_sec}/{total_min_sec}"

    @property
    def eta(self):
        if not self.duration_milliseconds or not self.location_milliseconds:
            return "Unknown"
        milliseconds_remaining = self.duration_milliseconds - self.location_milliseconds
        eta_datetime = utils.now_plus_milliseconds(milliseconds=milliseconds_remaining,
                                                   timezone_code=self._time_settings['timezone'])
        eta_string = utils.datetime_to_string(datetime_object=eta_datetime,
                                              template=("%H:%M" if self._time_settings['mil_time'] else "%I:%M %p"))
        return eta_string

    @property
    def title(self):
        if self._data.get('live'):
            return f"{self._data.get('grandparent_title', '')} - {self._data['title']}"
        elif self._data['media_type'] == 'episode':
            return f"{self._data.get('grandparent_title', '')} - S{self._data.get('parent_title', '').replace('Season ', '').zfill(2)}E{self._data.get('media_index', '').zfill(2)} - {self._data['title']}"
        else:
            return self._data.get('full_title')

    @property
    def status_icon(self):
        """
        Get icon for a stream state
        :return: emoji icon
        """
        return statics.switcher.get(self._data['state'], "")

    @property
    def type_icon(self):
        if self._data['media_type'] in statics.media_type_icons:
            return statics.media_type_icons[self._data['media_type']]
        # thanks twilsonco
        elif self._data.get('live'):
            return statics.media_type_icons['live']
        else:
            info("New media_type to pick icon for: {}: {}".format(self._data['title'], self._data['media_type']))
            return '🎁'

    @property
    def id(self):
        return self._data['session_id']

    @property
    def username(self):
        return self._data['username']

    @property
    def product(self):
        return self._data['product']

    @property
    def player(self):
        return self._data['player']

    @property
    def quality_profile(self):
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
    def transcoding_stub(self):
        return ' (Transcode)' if self.stream_container_decision == 'transcode' else ''

    @property
    def stream_container_decision(self):
        return self._data['stream_container_decision']

    def _session_title(self, session_number: int):
        return statics.session_title_message.format(count=statics.emoji_numbers[session_number - 1],
                                                    icon=self.status_icon, username=self.username,
                                                    media_type_icon=self.type_icon, title=self.title)

    def _session_player(self):
        return statics.session_player_message.format(product=self.product, player=self.player)

    def _session_details(self):
        return statics.session_details_message.format(quality_profile=self.quality_profile, bandwidth=self.bandwidth,
                                                      transcoding=self.transcoding_stub)

    def _session_progress(self):
        return statics.session_progress_message.format(progress=self.progress_marker, eta=self.eta)


class TautulliStreamInfo:
    def __init__(self, session: Session, session_number: int):
        self._session = session
        self._session_number = session_number

    @property
    def title(self):
        try:
            return self._session._session_title(session_number=self._session_number)
        except Exception as title_exception:
            return "Unknown"

    @property
    def player(self):
        return self._session._session_player()

    @property
    def details(self):
        return self._session._session_details()

    @property
    def progress(self):
        return self._session._session_progress()

    @property
    def body(self):
        try:
            return f"{self.player}\n{self.details}\n{self.progress}"
        except Exception as body_exception:
            error(body_exception)
            return f"Could not display data for session {self._session_number}"


class TautulliDataResponse:
    def __init__(self, overview_message: str, streams_info: List[TautulliStreamInfo] = None, plex_pass: bool = False,
                 error_occurred: bool = False):
        self._overview_message = overview_message
        self._streams = streams_info or []
        self.plex_pass = plex_pass
        self.error = error_occurred

    @property
    def embed(self):
        if len(self._streams) <= 0:
            return discord.Embed(title="No current activity")
        embed = discord.Embed(title=self._overview_message)
        for stream in self._streams:
            embed.add_field(name=stream.title, value=stream.body, inline=False)
        if self.plex_pass:
            embed.set_footer(text=f"To terminate a stream, react with the stream number.")
        return embed

    @property
    def message(self):
        if len(self._streams) <= 0:
            return "No current activity."
        final_message = f"{self._overview_message}\n"
        for stream in self._streams:
            final_message += f"{stream.title}\n{stream.body}\n"
        final_message += f"\nTo terminate a stream, react with the stream number."


class TautulliConnector:
    def __init__(self,
                 base_url: str,
                 api_key: str,
                 terminate_message: str,
                 analytics,
                 use_embeds: bool,
                 plex_pass: bool,
                 voice_channel_settings: dict,
                 time_settings: dict):
        self.base_url = base_url
        self.api_key = api_key
        self.api = tautulli.RawAPI(base_url=base_url, api_key=api_key)
        self.terminate_message = terminate_message
        self.analytics = analytics
        self.use_embeds = use_embeds
        self.plex_pass = plex_pass
        self.voice_channel_settings = voice_channel_settings
        self.time_settings = time_settings

    def _error_and_analytics(self, error_message, function_name):
        error(error_message)
        self.analytics.event(event_category="Error", event_action=function_name, random_uuid_if_needed=True)

    def refresh_data(self) -> Tuple[TautulliDataResponse, int, Union[Activity, None]]:
        """
        Parse activity JSON from Tautulli, prepare summary message for Discord
        :return: data wrapper, number of active streams and activity data
        """
        global session_ids
        data = self.api.activity()
        if data:
            debug(f"JSON returned by GET request: {data}")
            try:
                activity = Activity(activity_data=data, time_settings=self.time_settings)
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
                    if count >= 9:
                        break
                debug(f"Count: {count}")
                return TautulliDataResponse(overview_message=activity.message, streams_info=session_details,
                                            plex_pass=self.plex_pass), count, activity
            except KeyError as e:
                self._error_and_analytics(error_message=e, function_name='refresh_data (KeyError)')
        return TautulliDataResponse(overview_message="**Connection lost.**", error_occurred=True), 0, None

    def stop_stream(self, stream_number):
        """
        Stop a Plex stream
        :param stream_number: stream number used to react to Discord message (ex. 1, 2, 3)
        :return: Success/failure message
        """
        if stream_number not in session_ids.keys():
            return "**Invalid stream number.**"
        info(f"User attempting to stop session {stream_number}, id {session_ids[stream_number]}")
        try:
            if self.api.terminate_session(session_id=session_ids[stream_number], message=self.terminate_message):
                return f"Stream {stream_number} was stopped."
            else:
                return f"Stream {stream_number} could not be stopped."
        except Exception as e:
            self._error_and_analytics(error_message=e, function_name='stop_stream')
        return "Something went wrong."

    def get_library_id(self, library_name: str):
        for library in self.api.library_names:
            if library.get('section_name') == library_name:
                return library.get('section_id')
        error(f"Could not get ID for library {library_name}")
        return None

    def get_library_info(self, library_name: str):
        info(f"Collecting stats about library {library_name}")
        library_id = self.get_library_id(library_name=library_name)
        if not library_id:
            return None
        return self.api.get_library(section_id=library_id)

    def get_library_item_count(self, library_name: str):
        library_info = self.get_library_info(library_name=library_name)
        if not library_info:
            return 0
        if library_info.get('section_type') == 'artist':
            return library_info.get('child_count')  # child_count is the number of tracks
        return library_info.get('count', 0)
