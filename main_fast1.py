import asyncio
from playwright.async_api import async_playwright, TimeoutError
import discord
import os

# Discord bot token (keep this secure!)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')  # Use environment variable

# Discord channel ID where you want to send the message
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # Replace with your channel ID as an integer

# Function to extract data using Playwright
async def extract_data():
    url = 'https://www.op.gg/summoners/sg/Araaf-7870'

    async with async_playwright() as p:
        # Use Chrome channel if available, it's often faster than default Chromium
        browser = await p.chromium.launch(headless=True, channel="chrome")
        user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/115.0.0.0 Safari/537.36'
        )
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()

        # Navigate to the URL
        await page.goto(url)

        # Wait for all required elements within a single container to be available
        try:
            await page.wait_for_selector('div.name-container', timeout=10000)  # Adjust timeout as needed
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

# Discord client setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def send_discord_message():
    # Wait for data extraction to complete
    data = await extract_data()
    if data is None:
        message = "Failed to retrieve data."
    else:
        summoner_name, rank, lp = data
        message = f"**Summoner Name:** {summoner_name}\n**Rank:** {rank}\n**LP:** {lp}"

    # Send the message to the specified channel
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message)
        print("Message sent to Discord channel.")
    else:
        print("Failed to get the Discord channel. Check the CHANNEL_ID.")
    
    await client.close()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await send_discord_message()

# Run the Discord client and extraction concurrently
asyncio.run(client.run(DISCORD_TOKEN))