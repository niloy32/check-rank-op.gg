import asyncio
from playwright.async_api import async_playwright, TimeoutError
import discord
import os
import json

# Discord bot token and channel ID from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))


# Read previous data from last_data.json
def read_previous_data():
    try:
        with open('last_data.json', 'r') as f:
            previous_data = json.load(f)
        return previous_data
    except FileNotFoundError:
        # If the file doesn't exist, return None
        return None
    
# Write data to last_data.json
def write_current_data(data):
    with open('last_data.json', 'w') as f:
        json.dump(data, f)
        
# Function to extract data using Playwright
async def extract_data():
    url = 'https://www.op.gg/summoners/sg/Araaf-7870'

    async with async_playwright() as p:
        # Use Chromium browser
        browser = await p.chromium.launch(headless=True)
        user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/115.0.0.0 Safari/537.36'
        )
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()

        # Navigate to the URL
        await page.goto(url)

        # Wait for the required elements
        try:
            await page.wait_for_selector('div.name-container', timeout=10000)
            print("Name, Rank, and LP container found.")
        except TimeoutError:
            print("Required elements not found within timeout.")
            await browser.close()
            return None

        # Extract the summoner's name parts
        name_part = await page.inner_text('div.name-container h1 strong')
        tag_part = await page.inner_text('div.name-container h1 span')
        summoner_name = f"{name_part}{tag_part}"

        # Extract the rank and LP information
        rank = await page.inner_text('div.tier')
        lp = await page.inner_text('div.lp')

        await browser.close()
        return summoner_name.strip(), rank.strip(), lp.strip()

#compare rank
def compare_rank(prev_rank, current_rank):
    if prev_rank == current_rank:
        return "No change"
    else:
        return f"Changed from {prev_rank}"

def compare_lp(prev_lp, current_lp):
    # Extract numeric LP values
    prev_lp_value = int(prev_lp.split()[0])
    current_lp_value = int(current_lp.split()[0])

    lp_difference = current_lp_value - prev_lp_value
    if lp_difference == 0:
        return "No change"
    elif lp_difference > 0:
        return f"+{lp_difference} LP"
    else:
        return f"{lp_difference} LP"

async def main():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'Logged in as {client.user}')

        # Read previous data
        previous_data = read_previous_data()

        # Extract current data
        data = await extract_data()
        if data is None:
            message = "Failed to retrieve data."
        else:
            summoner_name, rank, lp = data

            # Prepare the message with comparison
            if previous_data:
                prev_rank = previous_data.get('rank')
                prev_lp = previous_data.get('lp')

                rank_change = compare_rank(prev_rank, rank)
                lp_change = compare_lp(prev_lp, lp)

                message = (
                    f"**Summoner Name:** {summoner_name}\n"
                    f"**Rank:** {rank} ({rank_change})\n"
                    f"**LP:** {lp} ({lp_change})"
                )
            else:
                message = (
                    f"**Summoner Name:** {summoner_name}\n"
                    f"**Rank:** {rank}\n"
                    f"**LP:** {lp}"
                )

            # Write current data to last_data.json
            current_data = {'summoner_name': summoner_name, 'rank': rank, 'lp': lp}
            write_current_data(current_data)

        # Send the message to the specified channel
        channel = client.get_channel(CHANNEL_ID)
        if channel is not None:
            await channel.send(message)
            print("Message sent to Discord channel.")
        else:
            print("Failed to get the Discord channel. Check the CHANNEL_ID.")

        # Close the Discord client after sending the message
        await client.close()

    await client.start(DISCORD_TOKEN)


if __name__ == '__main__':
    asyncio.run(main())
