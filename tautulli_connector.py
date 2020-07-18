import vars
import requests
import json
from logs import *
from decimal import *

session_ids = []


def selectIcon(state):
    """
    Get icon for a stream state
    :param state: stream state from Tautulli
    :return: emoji icon
    """
    return vars.switcher.get(state, "")


def build_overview_message(stream_count=0, transcode_count=0, total_bandwidth=0, lan_bandwidth=0):
    overview_message = ""
    if int(stream_count) > 0:
        overview_message += vars.sessions_message.format(stream_count=stream_count,
                                                         plural=('s' if int(stream_count) > 1 else ''))
    if transcode_count > 0:
        overview_message += f" ({vars.transcodes_message.format(transcode_count=transcode_count, plural=('s' if int(transcode_count) > 1 else ''))})"
    if total_bandwidth > 0:
        overview_message += f" | {vars.bandwidth_message.format(bandwidth=round(Decimal(float(total_bandwidth) / 1024), 1))}"
        if lan_bandwidth > 0:
            overview_message += f" ({vars.lan_bandwidth_message.format(bandwidth=round(Decimal(float(lan_bandwidth) / 1024), 1))}"
    return overview_message


def build_stream_message(session_data, count: int = 0, icon: str = "", username: str = "", title: str = "", product: str = "",
                         player: str = "", quality_profile: str = "", bandwidth: str = "0",
                         stream_container_decision: str = ""):
    if session_data['media_type'] == 'episode':
        title = f"{session_data.get('grandparent_title', '')} - S{session_data.get('parent_title', '').replace('Season ','').zfill(2)}E{session_data.get('media_index', '').zfill(2)} - {session_data['title']}"
    return f"{vars.session_title_message.format(count=count, icon=icon, username=username, title=title)}\n" \
           f"{vars.session_player_message.format(product=product, player=player)}\n" \
           f"{vars.session_details_message.format(quality_profile=quality_profile, bandwidth=(round(Decimal(float(bandwidth) / 1024), 1) if bandwidth != '' else '0'), transcoding=('(Transcode)' if stream_container_decision == 'transcode' else ''))}"


class TautulliConnector:
    def __init__(self, base_url, api_key, terminate_message):
        self.base_url = base_url
        self.api_key = api_key
        self.terminate_message = terminate_message

    def request(self, cmd, params=None):
        """
        Make an GET request to Tautulli's API
        :param cmd: Tautulli command
        :param params: Tautulli command parameters
        :return: request response
        """
        url = f"{self.base_url}/api/v2?apikey={self.api_key}{'&' + str(params) if params else ''}&cmd={cmd}"
        info(f"GET {url}")
        return requests.get(url=url)

    def refresh_data(self):
        """
        Parse activity JSON from Tautulli, prepare summary message for Discord
        :return: formatted summary message & number of active streams
        """
        global session_ids
        response = self.request("get_activity", None)
        if response:
            json_data = json.loads(response.text)
            info(f"JSON returned by GET request: {json_data}")
            try:
                stream_count = json_data['response']['data']['stream_count']
                transcode_count = json_data['response']['data']['stream_count_transcode']
                total_bandwidth = json_data['response']['data']['total_bandwidth']
                lan_bandwidth = json_data['response']['data']['lan_bandwidth']
                overview_message = build_overview_message(stream_count=stream_count, transcode_count=transcode_count,
                                                          total_bandwidth=total_bandwidth, lan_bandwidth=lan_bandwidth)
                sessions = json_data['response']['data']['sessions']
                count = 0
                session_ids = []
                final_message = f"{overview_message}\n"
                for session in sessions:
                    try:
                        count += 1
                        stream_message = build_stream_message(session_data=session, count=count, icon=selectIcon(session['state']),
                                                              username=session['username'],
                                                              title=session['full_title'],
                                                              product=session['product'], player=session['player'],
                                                              quality_profile=session['quality_profile'],
                                                              bandwidth=session['bandwidth'],
                                                              stream_container_decision=session[
                                                                  'stream_container_decision'])
                        final_message += f"\n{stream_message}\n"
                        session_ids.append(str(session['session_id']))
                    except ValueError as e:
                        error(e)
                        session_ids.append("000")
                        pass
                if int(stream_count) > 0:
                    final_message += f"\nTo terminate a stream, react with the stream number."
                info(f"Count: {count}\n"
                     f"Final message: {final_message}")
                return final_message, count
            except KeyError as e:
                error(e)
        return "**Connection lost.**", 0

    def stop_stream(self, stream_number):
        """
        Stop a Plex stream
        :param stream_number: stream number used to react to Discord message (ex. 1, 2, 3)
        :return: Success/failure message
        """
        info(f"User attempting to stop session {stream_number}, id {session_ids[stream_number]}")
        try:
            self.request('terminate_session',
                         f"session_id={session_ids[stream_number]}&message={self.terminate_message}")
            return f"Stream {stream_number} was ended"
        except Exception as e:
            error(e)
        return "Something went wrong."
