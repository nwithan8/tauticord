#!/usr/bin/env python3

import re
import json
import requests
import discord
from collections import defaultdict
from decimal import *
import math
import asyncio
import time

#Tautulli settings
TAUTULLI_URL = '' #http://[IP ADDRESS]:[PORT]
TAUTULLI_API_KEY = ''
TERMINATE_MESSAGE = ""
REFRESH_TIME = 15 #how often (seconds) the bot pulls new data. I'd recommend not making the bot ping Tautulli more often than every 5 seconds.

#Discord Settings
DISCORD_BOT_TOKEN = ''
BOT_OWNER_ID =  #Right-click on your profile picture -> "Copy ID"
DISCORD_CHANNEL_ID = #Right-click on the channel -> "Copy ID"
client = discord.Client()

#Numbers 1-9
emoji_numbers = [u"1\u20e3",u"2\u20e3",u"3\u20e3",u"4\u20e3",u"5\u20e3",u"6\u20e3",u"7\u20e3",u"8\u20e3",u"9\u20e3"]
session_ids = []

def request(cmd, params):
    return requests.get(TAUTULLI_URL + "/api/v2?apikey=" + TAUTULLI_API_KEY + "&" + str(params) + "&cmd=" + str(cmd)) if params != None else requests.get(TAUTULLI_URL + "/api/v2?apikey=" + TAUTULLI_API_KEY + "&cmd=" + str(cmd))

def add_reactions(message, count):
    for i in range(1,count):
        message.add_reaction(emoji_numbers[i-1])

async def stopStream(reaction, ids, tautulli_channel):
    loc = emoji_numbers.index(str(reaction.emoji))
    try:
        request('terminate_session','session_id=' + str(ids[loc]) + '&message=' + str(TERMINATE_MESSAGE))
        end_notification = await tautulli_channel.send(content="Stream " + str(loc+1) + " was ended.")
        await end_notification.delete(delay=1.0)
    except:
        end_notification = await tautulli_channel.send(content="Something went wrong.")
        await end_notification.delete(delay=1.0)

def selectIcon(state):
    switcher = {
        "playing":":arrow_forward:",
        "paused": ":pause_button:",
        "stopped": ":stop_button:",
        "buffering": ":large_blue_circle:",
    }
    return str(switcher.get(state, ""))

def refresh():
    global session_ids
    json_data = json.loads(request("get_activity",None).text)
    count = ""
    try:
        stream_count = json_data['response']['data']['stream_count']
        transcode_count = json_data['response']['data']['stream_count_transcode']
        total_bandwidth = json_data['response']['data']['total_bandwidth']
        lan_bandwidth = json_data['response']['data']['lan_bandwidth']
        overview_message = "Sessions: " + str(stream_count) + (" stream" if int(stream_count) == 1 else " streams") + ((" (" + str(transcode_count) + (" transcode" if int(transcode_count) == 1 else " transcodes") + ")") if int(transcode_count) > 0 else "") + ((" | Bandwidth: " + str(round(Decimal(float(total_bandwidth)/1024),1)) + " Mbps" + ((" (LAN: " + str(round(Decimal(float(lan_bandwidth)/1024),1)) + " Mbps)") if int(lan_bandwidth) > 0 else "")) if int(total_bandwidth) > 0 else "")
        sessions = json_data['response']['data']['sessions']
        count = 0
        session_ids = []
        final_message = overview_message + "\n"
        for session in sessions:
            try:
                count = count + 1
                stream_message = "**(" + str(count) + ")** " + selectIcon(str(session['state'])) + " " + str(session['username']) + ": *" + str(session["full_title"]) + "*\n"
                stream_message = stream_message + "__Player__: " + str(session['product']) + " (" + str(session['player']) + ")\n"
                stream_message = stream_message + "__Quality__: " + str(session['quality_profile']) + " (" + (str(round(Decimal(float(session['bandwidth'])/1024),1)) if session['bandwidth'] is not "" else "O") + " Mbps)" + (" (Transcode)" if str(session['stream_container_decision']) == 'transcode' else "")
                final_message = final_message + "\n" + stream_message + "\n"
                session_ids.append(str(session['session_id']))
            except ValueError:
                session_ids.append("000")
                pass
        if int(stream_count) > 0:
            final_message = final_message + "\n" + "To terminate a stream, react with the stream number."
        return final_message, count
    except KeyError:
        return "**Connection lost.**", 0
        
    
async def update(previous_message, tautulli_channel):
    data, count = refresh()
    await previous_message.delete()
    new_message = await tautulli_channel.send(content=data)
    for i in range(count):
        await new_message.add_reaction(emoji_numbers[i])
    bot_owner = client.get_user(BOT_OWNER_ID)
    reaction = ""
    user = ""
    def check(reaction, user):
        return user == bot_owner
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=float(REFRESH_TIME), check=check)
    except asyncio.TimeoutError:
        pass
    if reaction:
        if user.id == BOT_OWNER_ID:
            await stopStream(reaction, session_ids, tautulli_channel)
    return new_message

@client.event
async def on_ready():
    tautulli_channel = client.get_channel(DISCORD_CHANNEL_ID)
    #await tautulli_channel.send(content="Hello world!") #<---- UNCOMMENT AND RUN ONCE
    last_bot_message_id = ""
    async for msg in tautulli_channel.history(limit=100):
        if msg.author == client.user:
            last_bot_message_id = msg.id
            break
    message = await tautulli_channel.fetch_message(last_bot_message_id)
    while True:
        message = await update(message, tautulli_channel)

client.run(DISCORD_BOT_TOKEN)
