from playwright.async_api import async_playwright, TimeoutError
import discord
import os

# Discord bot token and channel ID from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

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
