import asyncio
from playwright.async_api import async_playwright, TimeoutError
import discord

# Discord bot token (keep this secure!)
DISCORD_TOKEN = 'MTMwMjI5NjYxNzMzNTkxODY5Mg.GDPwHT.Mhre7dGowMoHDfMrbixRewbWFTGZ28DRJZBcyo'

# Discord channel ID where you want to send the message
CHANNEL_ID = 735525142834446359  # Replace with your channel ID as an integer

# Function to extract data using Playwright
async def extract_data():
    url = 'https://www.op.gg/summoners/sg/Araaf-7870'

    async with async_playwright() as p:
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

        # Handle cookie consent or pop-ups
        try:
            consent_button = await page.wait_for_selector('button[class*="agree-button"]', timeout=5000)
            await consent_button.click()
            await page.wait_for_load_state('networkidle')
        except TimeoutError:
            pass  # No consent button found

        # Wait for the name, rank, and LP elements to be available
        try:
            await page.wait_for_selector('div.name-container h1', timeout=15000)
            await page.wait_for_selector('div.tier', timeout=15000)
            await page.wait_for_selector('div.lp', timeout=15000)
            print("Name, Rank, and LP elements found.")
        except TimeoutError:
            print("Required elements not found within timeout.")
            await browser.close()
            return None  # Return None if data is not available

        # Extract the summoner's name parts
        name_part = await page.inner_text('div.name-container h1 strong')
        tag_part = await page.inner_text('div.name-container h1 span')

        # Combine the name and tag
        summoner_name = f"{name_part}{tag_part}"

        # Extract the rank information
        rank = await page.inner_text('div.tier')
        lp = await page.inner_text('div.lp')

        # Close the browser
        await browser.close()

        return summoner_name.strip(), rank.strip(), lp.strip()

# Discord client setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Extract data
    data = await extract_data()
    if data is None:
        message = "Failed to retrieve data."
    else:
        summoner_name, rank, lp = data
        message = f"**Summoner Name:** {summoner_name}\n**Rank:** {rank}\n**LP:** {lp}"

    # Send the message to the specified channel
    channel = client.get_channel(CHANNEL_ID)
    if channel is not None:
        await channel.send(message)
        print("Message sent to Discord channel.")
    else:
        print("Failed to get the Discord channel. Check the CHANNEL_ID.")

    # Close the Discord client after sending the message
    await client.close()

# Run the Discord client
client.run(DISCORD_TOKEN)
