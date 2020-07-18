# Tauticord
A Discord bot that displays live data from Tautulli

# Features
Tauticord uses the Tautulli API to pull information from Tautulli and display them in a Discord channel, including:

OVERVIEW:
- Number of current streams
- Number of transcoding streams
- Total bandwidth
- Total LAN bandwidth

FOR EACH STREAM:
- Stream state (playing, paused, stopped, loading)
- User
- Media title
- Product and player
- Quality profile
- Stream bandwidth
- If stream is transcoding

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

# To come
This bot is still a work in progress. If you have any ideas for improving or adding to Tauticord, please do a pull request.
