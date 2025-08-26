import os
import json
import asyncio
import discord
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
# Load environment variables
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
SUMMONER_ID = os.getenv('SUMMONER_ID')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
PUUID = os.getenv('PUUID')

# Riot API endpoints
BASE_URL = 'https://sg2.api.riotgames.com'
#LEAGUE_ENDPOINT = f'/lol/league/v4/entries/by-summoner/{SUMMONER_ID}'
LEAGUE_ENDPOINT = f'/lol/league/v4/entries/by-puuid/{PUUID}'
SUMMONER_ENDPOINT = f'https://asia.api.riotgames.com/riot/account/v1/accounts/by-puuid/{PUUID}'
# File to store previous data
DATA_FILE = 'last_data.json'

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.check_rank()
        await self.close()
    
    async def check_rank(self):
        # Fetch current data
        current_data = get_rank_and_lp()
        if current_data is None:
            print("Failed to retrieve data.")
            return

        summoner_name, rank, lp, wins, losses, hot_streak = current_data
        previous_data = read_previous_data()

        # --- Helper functions (can be moved to utilities if desired) ---
        def parse_rank(r: str):
            if not r:
                return (-1, -1)
            parts = r.split()
            tier = parts[0]
            division = parts[1] if len(parts) > 1 else None
            tiers = ["Iron","Bronze","Silver","Gold","Platinum","Emerald","Diamond","Master","Grandmaster","Challenger"]
            divisions = ["IV","III","II","I"]  # Higher skill = lower index here, will invert later
            tier_idx = tiers.index(tier) if tier in tiers else -1
            if division and division in divisions:
                # Make higher divisions larger numerically for easy comparison
                division_value = 4 - (divisions.index(division) + 1)  # IV->0 ... I->3
            else:
                # For tiers without divisions (Master+), give max division value
                division_value = 4
            return (tier_idx, division_value)

        def compare_ranks(old_r: str, new_r: str):
            if not old_r or not new_r:
                return 0
            o = parse_rank(old_r)
            n = parse_rank(new_r)
            if n > o:
                return 1   # promotion
            if n < o:
                return -1  # demotion
            return 0

        # Check for rank or LP change
        rank_changed = False
        lp_changed = False
        rank_change_message = ""
        lp_change_message = ""
        promotion_state = 0  # 1 promotion, -1 demotion, 0 none
        if previous_data:
            prev_rank = previous_data['rank']
            prev_lp = previous_data['lp']
            if prev_rank != rank:
                rank_changed = True
                promotion_state = compare_ranks(prev_rank, rank)
                # We keep a neutral parenthetical; detailed text added later
                rank_change_message = f" (from {prev_rank} to {rank})"
            if prev_lp != lp:
                lp_changed = True
        else:
            # If no previous data, consider it a change
            rank_changed = True
            lp_changed = True

        # Build LP change message only if rank unchanged
        if lp_changed and not rank_changed and previous_data:
            lp_diff = lp - previous_data['lp']
            if lp_diff > 0:
                lp_change_message = f" (🔼 +{lp_diff} LP)"
            else:
                lp_change_message = f" (🔽 {lp_diff} LP)"

        # Special messaging on promotion / demotion
        promo_demo_message = ""
        if rank_changed:
            if promotion_state == 1:
                promo_demo_message = f"🎉 Promotion! Advanced from {previous_data['rank']} to {rank}. Starting LP: {lp}"
            elif promotion_state == -1:
                promo_demo_message = f"⚠️ Demoted from {previous_data['rank']} to {rank}. Adjusted LP: {lp}"
            else:
                # Different textual rank string but same evaluated position (edge case)
                promo_demo_message = f"Rank updated to {rank}."

        # Update data file
        write_current_data({
            'summoner_name': summoner_name,
            'rank': rank,
            'lp': lp,
            'wins': wins,
            'losses': losses,
            'hot_streak': hot_streak
        })

        # Compose final message
        lines = [f"Rank Update for Summoner: {summoner_name}"]
        if rank_changed:
            lines.append(f"Rank: {rank}{rank_change_message}")
        else:
            lines.append(f"Rank: {rank}")
        if not rank_changed:
            lines.append(f"LP: {lp}{lp_change_message}")
        else:
            # Avoid misleading negative LP change display after promotion/demotion
            lines.append(f"LP: {lp}")
        lines.append(f"Wins: {wins}")
        lines.append(f"Losses: {losses}")

        if promo_demo_message:
            lines.append(promo_demo_message)

        if hot_streak:
            lines.append(f"🔥 {summoner_name.split('#')[0]} is currently on a hot streak! 🔥")

        message = "\n".join(lines)
        print(message)

        # Check if we should send a message
        if rank_changed or lp_changed:
            await self.send_discord_message(message)
        else:
            print("No rank or LP change detected.")

        # Check if it's morning (e.g., 8 AM UTC) for daily synopsis
        current_time = datetime.now(timezone.utc)
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
                message += "\n🔥 King Araaf is currently on a hot streak! 🔥"

            await self.send_discord_message(message)
        else:
            print("It's not time for the daily synopsis.")

    async def send_discord_message(self, message):
        channel = self.get_channel(CHANNEL_ID)
        if channel:
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
    print("Summoner data:", summoner_data)

    name = summoner_data.get('gameName', 'Unknown Summoner')
    tagline = summoner_data.get('tagLine', 'no tag')
    summoner_name = f"{name}#{tagline}"

    # Get league entries
    response = requests.get(BASE_URL + LEAGUE_ENDPOINT, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching league data: {response.status_code}")
        return None

    data = response.json()
    print("League entries:", data)

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
    except (json.JSONDecodeError, FileNotFoundError):
        return {}
        
def write_current_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

intents = discord.Intents.default()
client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
