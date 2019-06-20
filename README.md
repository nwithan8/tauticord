# Tauticord
A Discord bot that displays live data from Tautulli

# Features
Tauticord uses the Tautulli API to pull information from Tautulli and displays it in a Discord channel, including:

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

# Setup
HOW TO MAKE A DISCORD BOT: https://discordpy.readthedocs.io/en/rewrite/discord.html

Run the following command to install the required Python packages:

	pip3 install discord PlexAPI requests asyncio

# Usage
Run the script with the following command:

	python3 Tauticord.py
	
**Important:** During each refresh, the bot finds and deletes its last message, replacing it with a new one. When the bot starts for the first time, there are no previous messages, which can cause it to error and quit.
Uncomment line 112 ( #await tautulli_channel.send(content="Hello world!") ) and run the bot once to get it to make an initial dummy message. You can then comment the line out again, and the bot should run as normal as long as there are previous messages from Tauticord in the Discord channel.

# To come
This bot is still a work in progress. If you have any ideas for improving or adding to Tauticord, please do a pull request. Make sure to also join my Discord server (https://discord.gg/47KN8bg) for questions or ideas about Tauticord.
