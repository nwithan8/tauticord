<div align="center">

# Tauticord

A Discord bot that displays live data from Tautulli

[![Release](https://img.shields.io/github/v/release/nwithan8/tauticord?color=yellow&include_prereleases&label=version&style=flat-square)](https://github.com/nwithan8/tauticord/releases)
[![Docker](https://img.shields.io/docker/pulls/nwithan8/tauticord?style=flat-square)](https://hub.docker.com/r/nwithan8/tauticord)
[![Licence](https://img.shields.io/github/license/nwithan8/tauticord?style=flat-square)](https://opensource.org/licenses/GPL-3.0)

<a href="https://www.buymeacoffee.com/nwithan8" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="19" width="95"></a>
[![GitHub Sponsors](https://img.shields.io/github/sponsors/nwithan8?style=flat-square)](https://github.com/sponsors/nwithan8)

<img src="https://raw.githubusercontent.com/nwithan8/tauticord/master/logo.png" alt="logo">

</div>

# Features

Tauticord uses the Tautulli API to pull information from Tautulli and display them in a Discord channel, including:

### Overview:

* Number of current streams
* Number of transcoding streams
* Total bandwidth
* Total LAN bandwidth
* Total remote bandwidth
* Library item counts

### For each stream:

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

<img src="https://raw.githubusercontent.com/nwithan8/tauticord/master/documentation/images/embed.png">

Administrator (the bot owner) can react to Tauticord's messages to terminate a specific stream (if they have Plex Pass).

Users can also indicate what libraries they would like monitored. Tauticord will create/update a voice channel for each
library name with item counts every hour.

<img src="https://raw.githubusercontent.com/nwithan8/tauticord/master/documentation/images/libraries.png">

# Installation and setup

## Requirements

- A Plex Media Server
- Tautulli (formerly known as PlexPy)
- A Discord server
- Docker
- [A Discord bot token](https://www.digitaltrends.com/gaming/how-to-make-a-discord-bot/)
    - Permissions required:
        - Manage Channels
        - View Channels
        - Send Messages
        - Manage Messages
        - Read Message History
        - Add Reactions
        - Manage Emojis
    - **Shortcut**: Use the following link to invite your bot to your server with the above permissions:
      https://discord.com/oauth2/authorize?client_id=YOUR_APPLICATION_ID&scope=bot&permissions=1073818704

Tauticord runs as a Docker container. The Dockerfile is included in this repository, or can be pulled
from [Docker Hub](https://hub.docker.com/r/nwithan8/tauticord)
or [GitHub Packages](https://github.com/nwithan8/tauticord/pkgs/container/tauticord).

### Volumes

You will need to map the following volumes:

| Host Path              | Container Path | Reason                                                                                            |
|------------------------|----------------|---------------------------------------------------------------------------------------------------|
| /path/to/logs/folder   | /logs          | Required, debug log file for bot will be generated here                                           |
| /path/to/config/folder | /config        | Optional, path to the folder containing the configuration file (override environmental variables) |

### Environmental Variables

You will need to set the following environment variables:

| Environment Variable            | Required | Value                                                                                                                                                                       | Example/Default                         |
|---------------------------------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| TC_DISCORD_BOT_TOKEN (required) | Yes      | Discord Bot Token                                                                                                                                                           | key from Discord Application above      |
| TC_DISCORD_SERVER_ID (required) | Yes      | Discord Server ID                                                                                                                                                           | ID, right-click server icon in Discord  |
| TC_TAUTULLI_URL (required)      | Yes      | IP of your Tautulli server                                                                                                                                                  | http://192.168.1.x:8181                 |
| TC_TAUTULLI_KEY (required)      | Yes      | API key for Tautulli server                                                                                                                                                 | abcd1234efgh5678ijkl9012mnop3456qrst    |
| TC_PLEX_PASS                    | No       | Enable PlexPass Features                                                                                                                                                    | "False"                                 |
| TC_REFRESH_SECONDS              | No       | Seconds between updates (5-second minimum built-in)                                                                                                                         | 15                                      |
| TC_TERMINATE_MESSAGE            | No       | Message sent to users when a stream is killed                                                                                                                               | "Your stream has ended."                |
| TC_SERVER_NAME                  | No       | Name of the Plex server.<br/>Will use provided; if not provided, will use "Plex"; if provided string is empty, will attempt to extract Plex Media Server name via Tautulli. | "Plex"                                  |
| TC_USE_24_HOUR_TIME             | No       | Whether to display times in 24-hour time                                                                                                                                    | "False"                                 |
| TC_HIDE_USERNAMES               | No       | Whether to hide usernames in the streams view                                                                                                                               | "False"                                 |
| TC_HIDE_PLATFORMS               | No       | Whether to hide platforms in the streams view                                                                                                                               | "False"                                 |
| TC_HIDE_PLAYER_NAMES            | No       | Whether to hide player names in the streams view                                                                                                                            | "False"                                 |
| TC_HIDE_QUALITY                 | No       | Whether to hide quality profiles in the streams view                                                                                                                        | "False"                                 |
| TC_HIDE_BANDWIDTH               | No       | Whether to hide bandwidth in the streams view                                                                                                                               | "False"                                 |
| TC_HIDE_TRANSCODE               | No       | Whether to hide transcoding statuses in the streams view                                                                                                                    | "False"                                 |
| TC_HIDE_PROGRESS                | No       | Whether to hide stream progress in the streams view                                                                                                                         | "False"                                 |
| TC_HIDE_ETA                     | No       | Whether to hide stream ETAs in the streams view                                                                                                                             | "False"                                 | |          |                                                                                                                                                                             |                                         |
| TC_VC_STATS_CATEGORY_NAME       | No       | Name of the stats voice channel category                                                                                                                                    | "Tautulli Stats"                        |
| TC_VC_STREAM_COUNT              | No       | Whether to display current stream count in a voice channel                                                                                                                  | "False"                                 |
| TC_VC_TRANSCODE_COUNT           | No       | Whether to display current transcode count in a voice channel                                                                                                               | "False"                                 |
| TC_VC_BANDWIDTH                 | No       | Whether to display current bandwidth in a voice channel                                                                                                                     | "False"                                 |
| TC_VC_LOCAL_BANDWIDTH           | No       | Whether to display current local bandwidth in a voice channel                                                                                                               | "False"                                 |
| TC_VC_REMOTE_BANDWIDTH          | No       | Whether to display current remote bandwidth in a voice channel                                                                                                              | "False"                                 |
| TC_VC_PLEX_STATUS               | No       | Whether to display Plex online status in a voice channel                                                                                                                    | "False"                                 |
| TC_VC_LIBRARIES_CATEGORY_NAME   | No       | Name of the libraries voice channel category                                                                                                                                | "Tautulli Libraries"                    |                                  
| TC_VC_LIBRARY_STATS             | No       | Whether to display library statistics in voice channels                                                                                                                     | "False"                                 |
| TC_VC_LIBRARY_NAMES             | No       | Comma-separated list of libraries to display statistics of                                                                                                                  | "Movies,TV Shows,Music"                 |       
| TC_VC_LIBRARY_REFRESH_SECONDS   | No       | Seconds between updates (5-minute minimum built-in)                                                                                                                         | 3600                                    |
| TC_VC_TV_SERIES_COUNT           | No       | Display series counts for all selected "TV Shows" libraries                                                                                                                 | "True"                                  |
| TC_VC_TV_EPISODE_COUNT          | No       | Display episode counts for all selected "TV Shows" libraries                                                                                                                | "True"                                  |
| TC_VC_MUSIC_ARTIST_COUNT        | No       | Display artist counts for all selected "Music" libraries                                                                                                                    | "True"                                  |
| TC_VC_MUSIC_TRACK_COUNT         | No       | Display track counts for all selected "Music" libraries                                                                                                                     | "True"                                  |
| TC_DISCORD_ADMIN_IDS            | No       | List of Discord IDs with admin privileges                                                                                                                                   | ID, right-click user profile in Discord |
| TC_DISCORD_CHANNEL_NAME         | No       | Channel name for updates                                                                                                                                                    | "Tautulli Status"                       |
| TC_DISCORD_NITRO                | No       | Whether the Discord server has a Nitro subscription (bot will upload custom emojis)                                                                                         | "False"                                 |
| TC_ALLOW_ANALYTICS              | No       | Allow Anonymous Crash Analytics?                                                                                                                                            | "True"                                  |                
| TC_VC_PERFORMANCE_CATEGORY_NAME | No       | Name of the performance voice channel category                                                                                                                              | "Performance"                  |
| TC_MONITOR_CPU                  | No       | Whether to monitor CPU performance (see [Performance Monitoring](#performance-monitoring))                                                                                  | "False"                                 |
| TC_MONITOR_MEMORY               | No       | Whether to monitor RAM performance (see [Performance Monitoring](#performance-monitoring))                                                                                  | "False"                                  |
| TZ                              | No       | Timezone that your server is in                                                                                                                                             | "America/New_York"                      |

You can also set these variables via a configuration file:

1. Map the `/config` directory (see volumes above)
2. Enter the mapped directory on your host machine
3. Rename the ``config.yaml.example`` file in the path to ``config.yaml``
4. Complete the variables in ``config.yaml``

Please note, if the `config.yaml` file is present, the application will ONLY use this file for
configuration. If you are going to use it, you need to fill it out in its entirety.

## Run without Docker

You can run Tauticord outside of Docker by cloning this repository and either:

- renaming `config.yaml.example` to `config.yaml`, filling out the settings inside `config.yaml` and running the bot
  with `python3 run.py --config config.yaml`
- adding the above environmental variables to your system and running the bot with `python3 run.py`

Please note, this is NOT ADVISED. Running this application as a Docker container is the only officially-supported method
of running Tauticord.

# Common Issues

- On startup, Tauticord attempts to upload a set of custom emojis that it will use when displaying stream information (
  if they do not already exist). Your bot will need to have the `Manage Emojis` permission in order to do this.
    - Discord has a limit of 50 custom emojis per server. If you have reached this limit, you will need to remove some
      of your existing emojis before Tauticord can upload its own.
    - If you do not want to remove any of your existing emojis, Tauticord will simply skip uploading its own emojis and
      use the default emojis that Discord provides instead.

# Analytics

Tauticord uses Google Analytics to collect statistics such as common errors that will help with future development.
**This data is limited, anonymous, and never sold or redistributed.**

**When and what data is collected?**

- Whenever the bot comes online
    - What operating system the bot is running on (Windows, Linux, MacOS, etc.)
- Whenever an error is logged
    - What function the error occurred in.

**What data is NOT collected:**

- Any identifying information about the user
- Any identifying information about the computer/machine (a random ID is generated on each analytics call, IP addresses
  are anonymized)
- Settings for Discord or Tautulli, including passwords, API tokens, URLs, etc.
- Any data from Tautulli
- Anything typed in Discord.

# Performance Monitoring

Tauticord will attempt to query the system it is running on for CPU and RAM usage every 5 minutes.

Tautulli does not currently offer a way to query performance statistics from its API. As a result, this data is **not Tautulli-specific performance data**, but rather **the performance of the system that Tauticord is running on**. 

If Tauticord is running on the same system as Tautulli, then this data may reflect the performance of Tautulli (+ Tauticord and all other processes running on the system).

If Tauticord is running on a different system than Tautulli, or is running isolated in a Docker container, then this data will not reflect the performance of Tautulli.

# Development

This bot is still a work in progress. If you have any ideas for improving or adding to Tauticord, please open an issue
or a pull
request.

# Contact

Please leave a pull request if you would like to contribute.

Follow me on Twitter: [@nwithan8](https://twitter.com/nwithan8)

Also feel free to check out my other projects here on [GitHub](https://github.com/nwithan8) or join the #developer
channel in my Discord server below.

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
        <a href=https://github.com/benwaco>
            <img src=https://avatars.githubusercontent.com/u/127471645?v=4 width="50;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=benwaco/>
            <br />
            <sub style="font-size:14px"><b>benwaco</b></sub>
        </a>
    </td>
</tr>
<tr>
    <td align="center" style="word-wrap: break-word; width: 75.0; height: 75.0">
        <a href=https://github.com/tdurieux>
            <img src=https://avatars.githubusercontent.com/u/5577568?v=4 width="50;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Thomas Durieux/>
            <br />
            <sub style="font-size:14px"><b>Thomas Durieux</b></sub>
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
