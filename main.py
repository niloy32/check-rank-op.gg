import os
import json
import asyncio
import discord
from discord.ext import tasks
import requests
from datetime import datetime

# Load environment variables
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
SUMMONER_ID = os.getenv('SUMMONER_ID')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
PUUID = os.getenv('PUUID')

# Riot API endpoints
BASE_URL = 'https://sg2.api.riotgames.com'
LEAGUE_ENDPOINT = f'/lol/league/v4/entries/by-summoner/{SUMMONER_ID}'
SUMMONER_ENDPOINT = f'https://asia.api.riotgames.com/riot/account/v1/accounts/by-puuid/{PUUID}'

# File to store previous data
DATA_FILE = 'last_data.json'

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        # Start the background task
        self.check_rank.start()

    @tasks.loop(minutes=60)
    async def check_rank(self):
        # Fetch current data
        current_data = get_rank_and_lp()
        if current_data is None:
            print("Failed to retrieve data.")
            return

        summoner_name, rank, lp, wins, losses, hot_streak = current_data
        previous_data = read_previous_data()

        # Check for rank or LP change
        rank_changed = False #testing
        lp_changed = False #testing
        if previous_data:
            if previous_data['rank'] != rank:
                rank_changed = True
            if previous_data['lp'] != lp:
                lp_changed = True
        else:
            rank_changed = True
            lp_changed = True

        # Update data file
        write_current_data({
            'summoner_name': summoner_name,
            'rank': rank,
            'lp': lp,
            'wins': wins,
            'losses': losses,
            'hot_streak': hot_streak
        })

        # Check if we should send a message
        message = None
        if rank_changed or lp_changed:
            message = (
                f"**Rank Update for Summoner:** {summoner_name}\n"
                f"**Rank:** {rank}\n"
                f"**LP:** {lp}\n"
                f"**Wins:** {wins}\n"
                f"**Losses:** {losses}"
            )

            # Check for hot streak
            if hot_streak:
                message += "\n 🔥 King Araaf is currently on a hot streak! 🔥"

            await self.send_discord_message(message)

        # Check if it's morning (e.g., 8 AM UTC) for daily synopsis
        current_time = datetime.utcnow()
        if current_time.hour == 8:
            message = (
                f"**Daily Synopsis for {summoner_name}:**\n"
                f"**Rank:** {rank}\n"
                f"**LP:** {lp}\n"
                f"**Wins:** {wins}\n"
                f"**Losses:** {losses}"
            )

            # Include hot streak in daily synopsis
            if hot_streak:
                message += "\n  🔥 King Araaf is currently on a hot streak! 🔥"

            await self.send_discord_message(message)

    @check_rank.before_loop
    async def before_check_rank(self):
        await self.wait_until_ready()
        print("Bot is ready and starting the rank check loop.")

    async def send_discord_message(self, message):
        channel = self.get_channel(CHANNEL_ID)
        if channel is not None:
            await channel.send(message)
            print("Message sent to Discord channel.")
        else:
            print("Failed to get the Discord channel. Check the CHANNEL_ID.")

def get_rank_and_lp():
    headers = {'X-Riot-Token': RIOT_API_KEY}
    
    # Get summoner name
    response_summoner = requests.get(SUMMONER_ENDPOINT, headers=headers)
    if response_summoner.status_code != 200:
        print(f"Error fetching summoner data: {response_summoner.status_code}")
        return None
    summoner_data = response_summoner.json()
    print("summoner_data- ",summoner_data)

    name = summoner_data.get('gameName', 'Unknown Summoner')
    tagline = summoner_data.get('tagLine', 'no tag')
    summoner_name = name+'#'+tagline

    # Get league entries
    response = requests.get(BASE_URL + LEAGUE_ENDPOINT, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching league data: {response.status_code}")
        return None

    data = response.json()
    print("league entries- ",data)

    # Assuming we're interested in ranked solo queue
    for entry in data:
        if entry['queueType'] == 'RANKED_SOLO_5x5':
            rank = f"{entry['tier'].title()} {entry['rank']}"
            lp = entry['leaguePoints']
            wins = entry['wins']
            losses = entry['losses']
            hot_streak = entry['hotStreak']
            return summoner_name, rank, lp, wins, losses, hot_streak
    return None

def read_previous_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def write_current_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

intents = discord.Intents.default()
client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
