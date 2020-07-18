# Numbers 1-9
emoji_numbers = [u"1\u20e3", u"2\u20e3", u"3\u20e3", u"4\u20e3", u"5\u20e3", u"6\u20e3", u"7\u20e3", u"8\u20e3",
                 u"9\u20e3"]

switcher = {
        "playing": ":arrow_forward:",
        "paused": ":pause_button:",
        "stopped": ":stop_button:",
        "buffering": ":large_blue_circle:",
}

sessions_message = """{stream_count} stream{plural}"""
transcodes_message = """{transcode_count} transcode{plural}"""
bandwidth_message = """{bandwidth} Mbps"""
lan_bandwidth_message = """{bandwidth} Mbps"""

session_title_message = """**({count})** {icon} {username}: *{title}*"""
session_player_message = """__Player__: {product} ({player})"""
session_details_message = """__Quality__: {quality_profile} ({bandwidth} Mbps) {transcoding}"""
