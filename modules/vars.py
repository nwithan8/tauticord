# Numbers 1-9
emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣" ,"5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

switcher = {
        "playing": "▶️",
        "paused": "⏸",
        "stopped": "⏹",
        "buffering": "⏳",
        "error": "⚠️"
}
sessions_message = """{stream_count} stream{plural}"""
transcodes_message = """{transcode_count} transcode{plural}"""
bandwidth_message = """🌐 {bandwidth}"""
lan_bandwidth_message = """(🏠 {bandwidth})"""

session_title_message = """{count}—{icon} {media_type_icon} {username}: *{title}*"""
session_player_message = """__Player__: {product} ({player})"""
session_details_message = """__Quality__: {quality_profile} ({bandwidth}){transcoding}"""
