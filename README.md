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

# Requirements
- A Plex Media Server
- Tautulli (formerly known as PlexPy)
- A Discord server
- Python 3.7+

# Installation and setup
HOW TO MAKE A DISCORD BOT: https://www.digitaltrends.com/gaming/how-to-make-a-discord-bot/

Install requirements with:

	pip3 install -r requirements.txt

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
