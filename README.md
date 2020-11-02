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

### MODIIFIED FROM nwithan8's version in the following ways:
* Faster and more efficient thanks to minimal communication with Discord
    * Edit a single message with updated information rather than delete and replace (but replace if message isn't the bottom-most message in the channel)
    * Only edit/add message if message contents differ from previous message, so almost all communication with Discord is eliminated
    * Add/remove individual reactions only when neessary
* Use of embeds (optional) and more symbols for more aesthetic output
* Use convenient units for bitrate reporting
* Include media type in stream info

Administrator (the bot owner) can react to Tauticord's messages to terminate a specific stream.

# Requirements
- A Plex Media Server
- Tautulli (formerly known as PlexPy)
- A Discord server

# Installation and setup
HOW TO MAKE A DISCORD BOT: https://www.digitaltrends.com/gaming/how-to-make-a-discord-bot/

Run the pip command at the top of the PlexRecs.py file to install the required Python packages:

	pip3 install discord requests asyncio

Copy ``config.py.sample`` to ``config.py`` and complete the variables in the file.

# Usage
Run the script with the following command:

	python3 Tauticord.py
	
# Docker
You can also run Tauticord as a Docker container.

After copying and editing your ``config.py`` file, build the container with:
	``docker build -t tauticord .``
Run the container with ``docker run tauticord``

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
