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
- Python 3.7+

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
	
# Docker
You can also run Tauticord as a Docker container.

After copying and editing your ``config.py`` file, build the container with:
	``docker build -t tauticord .``
Run the container with ``docker run tauticord``

# UnRaid
You can also run Tauticord as a docker template on UnRaid

1. Create a new Discord Application [here](https://discordapp.com/developers/applications). Note the Application ID, it will be needed in step 2
2. Copy this URL, update replace with your ApplicationID, then paste into a browser, and confirm permissions to add bot to your server. 

https://discord.com/api/oauth2/authorize?client_id=<YOUR_APPLICATION_ID_HERE>&permissions=522304&scope=bot%20applications.commands

3. After installing from Unraid Community Applications from DockerHub, update the following Environment Variables:

| Environment Variable  | Value |  Example/Default |
| ------------- | ------------- | ------------- |
| TAUTULLI_IP (required)  | IP of your Tautulli server | http://192.168.1.x:8181 |
| TAUTULLI_API_KEY (required) | API key for Tautulli server  | abcd1234efgh5678ijkl9012mnop3456qrst  |
| TC_PLEXPASS | Enable PlexPass Features | true |
| TC_REFRESH_SEC | Seconds between updates | 15 |
| TC_LIBRARY | Libraries to monitor | Movies,TV Shows | 
| TC_DISCORD_BOT_TOKEN (required) | Discord Bot Token | <key from DiscordApplication above> |
| TC_DISCORD_SERVER_ID (required) | Discord Server ID | <ID, right-click server> |
| TC_DISCORD_OWNER_ID | Your Discord ID for PlexPass Features | <ID, right-click profile> |
| TC_DISCORD_CHANNELNAME | Channel name for updates | tautulli |
| TC_DISCORD_USEEMBEDS | Use embedded messages rather than regular text chat | true |
| TC_CHANNELS | Voice Channel Enable: Stream Count, Transcode Count, Bandwidth, Library Stats | false,false,false,false | 
| TC_ANALYTICS | Allow Anonymous Crash Analytics? | true |

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
