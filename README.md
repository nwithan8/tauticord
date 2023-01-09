[![Donate with Bitcoin](https://en.cryptobadges.io/badge/micro/3H94aowuz4hgbvNjceZ2xeq14rjmGz4cD9)](https://en.cryptobadges.io/donate/3H94aowuz4hgbvNjceZ2xeq14rjmGz4cD9)

# Tauticord
A Discord bot that displays live data from Tautulli

# Features
Tauticord uses the Tautulli API to pull information from Tautulli and display them in a Discord channel, including:

### OVERVIEW:
* Number of current streams
* Number of transcoding streams
* Total bandwidth
* Total LAN bandwidth

### FOR EACH STREAM:
* Stream state (playing, paused, stopped, loading)
* Media type (tv show/movie/song/photo)
* User
* Media title
* Product and player
* Quality profile
* Stream bandwidth
* If stream is transcoding
* Progress of stream
* ETA of stream completion

Administrator (the bot owner) can react to Tauticord's messages to terminate a specific stream (if they have Plex Pass).

Users can also indicate what libraries they would like monitored. Tauticord will create/update a voice channel for each library name with item counts every hour.

# Requirements
- A Plex Media Server
- Tautulli (formerly known as PlexPy)
- A Discord server
- Python 3.10+

# Installation and setup
HOW TO MAKE A DISCORD BOT: https://www.digitaltrends.com/gaming/how-to-make-a-discord-bot/
Permissions required:
- Manage Channels
- View Channels
- Send Messages
- Manage Messages
- Read Message History
- Add Reactions

Install requirements with:

	pip3 install -r requirements.txt

Copy ``config.yaml.example`` to ``config.yaml`` and complete the variables in the file.

# Usage
Run the script with the following command:

	python3 Tauticord.py

Because the script is configured to quit if internet connectivity issues occur, it is HIGHLY RECOMMENDED to run this application as a Docker container (see below). The Docker container is configured to automatically restart the bot if an internet connection is lost.
	
# Docker
You can also run Tauticord as a Docker container. The Dockerfile is included in this repository, or can be pulled from [Docker Hub](https://hub.docker.com/r/nwithan8/tauticord) or [GitHub Packages](https://github.com/nwithan8/tauticord/pkgs/container/tauticord).

You will need to set the following environment variables:

| Environment Variable            | Value                                                          | Example/Default                      |
|---------------------------------|----------------------------------------------------------------|--------------------------------------|
| TC_TAUTULLI_URL (required)      | IP of your Tautulli server                                     | http://192.168.1.x:8181              |
| TC_TAUTULLI_KEY (required)      | API key for Tautulli server                                    | abcd1234efgh5678ijkl9012mnop3456qrst |
| TC_PLEX_PASS                    | Enable PlexPass Features                                       | "False"                              |
| TC_REFRESH_SECONDS              | Seconds between updates (5-second minimum built-in)            | 15                                   |
| TC_TERMINATE_MESSAGE            | Message sent to users when a stream is killed                  | "Your stream has ended."             |
| TC_USE_24_HOUR_TIME             | Whether to display times in 24-hour time                       | "False"                              |
| TC_VC_STATS_CATEGORY_NAME       | Name of the stats voice channel category                       | "Tautulli Stats"                     |
| TC_VC_STREAM_COUNT              | Whether to display current stream count in a voice channel     | "False"                              |
| TC_VC_TRANSCODE_COUNT           | Whether to display current transcode count in a voice channel  | "False"                              |
| TC_VC_BANDWIDTH                 | Whether to display current bandwidth in a voice channel        | "False"                              |
| TC_VC_LOCAL_BANDWIDTH           | Whether to display current local bandwidth in a voice channel  | "False"                              |
| TC_VC_REMOTE_BANDWIDTH          | Whether to display current remote bandwidth in a voice channel | "False"                              |
| TC_VC_PLEX_STATUS               | Whether to display Plex online status in a voice channel       | "False"                              |
| TC_VC_LIBRARIES_CATEGORY_NAME   | Name of the libraries voice channel category                   | "Tautulli Libraries"                 |                                  
| TC_VC_LIBRARY_STATS             | Whether to display library statistics in voice channels        | "False"                              |
| TC_VC_LIBRARY_NAMES             | Comma-separated list of libraries to display statistics of     | "Movies,TV Shows,Music"              |       
| TC_VC_LIBRARY_REFRESH_SECONDS   | Seconds between updates (5-minute minimum built-in)            | 3600                                 |
| TC_DISCORD_BOT_TOKEN (required) | Discord Bot Token                                              | <key from DiscordApplication above > |
| TC_DISCORD_SERVER_ID (required) | Discord Server ID                                              | <ID, right-click server>             |
| TC_DISCORD_ADMIN_IDS            | List of Discord IDs with admin privileges                      | <ID, right-click profile>            |
| TC_DISCORD_CHANNEL_NAME         | Channel name for updates                                       | "Tautulli Status"                    |
| TC_USE_EMBEDS                   | Use embedded messages rather than regular text chat            | "True"                               |
| TC_ALLOW_ANALYTICS              | Allow Anonymous Crash Analytics?                               | "True"                               |                
| TZ                              | Timezone that your server is in                                | "America/New_York"                   |

# Analytics
Tauticord uses Google Analytics to collect statistics such as common errors that will help with future development.
**This data is limited, anonymous, and never sold or redistributed.**

**When and what data is collected?**
- Whenever the bot comes online
	- What operating system the bot is running on (Windows, Linux, MacOS, etc.)
- Whenever an error is logged
 	- What Python function the error occurred in.

**What data is NOT collected:**
- Any identifying information about the user
- Any identifying information about the computer/machine (a random ID is generated on each analytics call, IP addresses are anonymized)
- Settings for Discord or Tautulli, including passwords, API tokens, URLs, etc.
- Any data from Tautulli
- Anything typed in Discord.

# To come
This bot is still a work in progress. If you have any ideas for improving or adding to Tauticord, please do a pull request.

# Contact
Please leave a pull request if you would like to contribute.

Follow me on Twitter: [@nwithan8](https://twitter.com/nwithan8)

Also feel free to check out my other projects here on [GitHub](https://github.com/nwithan8) or join the #developer channel in my Discord server below.

<div align="center">
	<p>
		<a href="https://discord.gg/ygRDVE9"><img src="https://discordapp.com/api/guilds/472537215457689601/widget.png?style=banner2" alt="" /></a>
	</p>
</div>

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

### Contributors

<table>
<tr>
    <td align="center" style="word-wrap: break-word; width: 75.0; height: 75.0">
        <a href=https://github.com/nwithan8>
            <img src=https://avatars.githubusercontent.com/u/17054780?v=4 width="50;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Nate Harris/>
            <br />
            <sub style="font-size:14px"><b>Nate Harris</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 75.0; height: 75.0">
        <a href=https://github.com/TomW1605>
            <img src=https://avatars.githubusercontent.com/u/17092573?v=4 width="50;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Thomas White/>
            <br />
            <sub style="font-size:14px"><b>Thomas White</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 75.0; height: 75.0">
        <a href=https://github.com/twilsonco>
            <img src=https://avatars.githubusercontent.com/u/7284371?v=4 width="50;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Tim Wilson/>
            <br />
            <sub style="font-size:14px"><b>Tim Wilson</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 75.0; height: 75.0">
        <a href=https://github.com/Yoruio>
            <img src=https://avatars.githubusercontent.com/u/38411921?v=4 width="50;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Roy Du/>
            <br />
            <sub style="font-size:14px"><b>Roy Du</b></sub>
        </a>
    </td>
</tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
