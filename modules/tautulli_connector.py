import modules.vars as vars
import requests
import json
import discord
from modules.logs import *
from decimal import *

session_ids = []


def humanbitrate(B,d = 1):
    # 'Return the given bytes as a human friendly kbps, mbps, gbps, or tbps string'
    # Next line altered so that this takes in kilobytes instead of bytes
	B = float(B) * 1024
	KB = float(1024)
	MB = float(KB ** 2) # 1,048,576
	GB = float(KB ** 3) # 1,073,741,824
	TB = float(KB ** 4) # 1,099,511,627,776
	
	if d <= 0:
		if B < KB:
			return '{0} bps'.format(int(B))
		elif KB <= B < MB:
			return '{0:d} kbps'.format(int(B/KB))
		elif MB <= B < GB:
			return '{0:d} Mbps'.format(int(B/MB))
		elif GB <= B < TB:
			return '{0:d} Gbps'.format(int(B/GB))
		elif TB <= B:
			return '{0:d} Tbps'.format(int(B/TB))
	else:
		if B < KB:
			return '{0} bps'.format(B)
		elif KB <= B < MB:
			return '{0:d} kbps'.format(int(B/KB), nd = d)
		elif MB <= B < GB:
			return '{0:.{nd}f} Mbps'.format(B/MB, nd = d)
		elif GB <= B < TB:
			return '{0:.{nd}f} Gbps'.format(B/GB, nd = d)
		elif TB <= B:
			return '{0:.{nd}f} Tbps'.format(B/TB, nd = d)

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
    # if total_bandwidth > 0:
    #     overview_message += f" | {vars.bandwidth_message.format(bandwidth=round(Decimal(float(total_bandwidth) / 1024), 1))}"
    #     if lan_bandwidth > 0:
    #         overview_message += f" ({vars.lan_bandwidth_message.format(bandwidth=round(Decimal(float(lan_bandwidth) / 1024), 1))}"
    if total_bandwidth > 0:
        overview_message += f" | {vars.bandwidth_message.format(bandwidth=humanbitrate(float(total_bandwidth)))}"
        if lan_bandwidth > 0:
            overview_message += f" {vars.lan_bandwidth_message.format(bandwidth=humanbitrate(float(lan_bandwidth)))}"
    return overview_message


def build_stream_message(session_data, count: int = 0, icon: str = "", username: str = "", title: str = "", product: str = "",
                         player: str = "", quality_profile: str = "", bandwidth: str = "0",
                         stream_container_decision: str = ""):
    
    if session_data['media_type'] == 'episode':
        title = f"{session_data.get('grandparent_title', '')} - S{session_data.get('parent_title', '').replace('Season ','').zfill(2)}E{session_data.get('media_index', '').zfill(2)} - {session_data['title']}"
    media_type_icons = {'episode': '📺', 'track': '🎧', 'movie': '🎞', 'clip': '🎬', 'photo': '🖼'}
    if session_data['media_type'] in media_type_icons:
        media_type_icon = media_type_icons[session_data['media_type']]
    else:
        media_type_icon = '🎁'
        info("New media_type to pick icon for: {}: {}".format(session_data['title'], session_data['media_type']))
    return f"{vars.session_title_message.format(count=vars.emoji_numbers[count-1], icon=icon, username=username, media_type_icon=media_type_icon, title=title)}\n" \
           f"{vars.session_player_message.format(product=product, player=player)}\n" \
           f"{vars.session_details_message.format(quality_profile=quality_profile, bandwidth=(humanbitrate(float(bandwidth)) if bandwidth != '' else '0'), transcoding=('(Transcode)' if stream_container_decision == 'transcode' else ''))}"
           # f"{vars.session_details_message.format(quality_profile=quality_profile, bandwidth=(round(Decimal(float(bandwidth) / 1024), 1) if bandwidth != '' else '0'), transcoding=('(Transcode)' if stream_container_decision == 'transcode' else ''))}"


class TautulliConnector:
    def __init__(self, base_url, api_key, terminate_message, analytics, use_embeds, plex_pass):
        self.base_url = base_url
        self.api_key = api_key
        self.terminate_message = terminate_message
        self.analytics = analytics
        self.use_embeds = use_embeds
        self.plex_pass = plex_pass

    def _error_and_analytics(self, error_message, function_name):
        error(error_message)
        self.analytics.event(event_category="Error", event_action=function_name, random_uuid_if_needed=True)

    def request(self, cmd, params=None):
        """
        Make an GET request to Tautulli's API
        :param cmd: Tautulli command
        :param params: Tautulli command parameters
        :return: request response
        """
        url = f"{self.base_url}/api/v2?apikey={self.api_key}{'&' + str(params) if params else ''}&cmd={cmd}"
        debug(f"GET {url}")
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
            debug(f"JSON returned by GET request: {json_data}")
            try:
                stream_count = json_data['response']['data']['stream_count']
                transcode_count = json_data['response']['data']['stream_count_transcode']
                total_bandwidth = json_data['response']['data']['total_bandwidth']
                lan_bandwidth = json_data['response']['data']['lan_bandwidth']
                overview_message = build_overview_message(stream_count=stream_count, transcode_count=transcode_count, total_bandwidth=total_bandwidth, lan_bandwidth=lan_bandwidth)
                sessions = json_data['response']['data']['sessions']
                count = 0
                session_ids = []
                if self.use_embeds:
                    e = discord.Embed(title=overview_message)
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
                                                                      'stream_container_decision']).split('\n')
                            e.add_field(name=stream_message[0], value='\n'.join(stream_message[1:]), inline=False)
                            session_ids.append(str(session['session_id']))
                        except ValueError as e:
                            self._error_and_analytics(error_message=e, function_name='refresh_data (ValueError)')
                            session_ids.append("000")
                            pass
                        if count >= 9:
                            break
                    if int(stream_count) > 0:
                        if self.plex_pass:
                            e.set_footer(text=f"\nTo terminate a stream, react with the stream number.")
                    else:
                        e = discord.Embed(title="No current activity")
                    debug(f"Count: {count}")
                    return e, count
                else:
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
                            self._error_and_analytics(error_message=e, function_name='refresh_data (ValueError)')
                            session_ids.append("000")
                            pass
                        if count >= 9:
                            break
                    if int(stream_count) > 0:
                        if self.plex_pass:
                            final_message += f"\nTo terminate a stream, react with the stream number."
                    else:
                        final_message = "No current activity."
                    debug(f"Count: {count}\n"
                         f"Final message: {final_message}")
                    return final_message, count
            except KeyError as e:
                self._error_and_analytics(error_message=e, function_name='refresh_data (KeyError)')
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
            self._error_and_analytics(error_message=e, function_name='stop_stream')
        return "Something went wrong."
