# League Rank Notifier

This project is a Discord bot that monitors a League of Legends player's rank and LP (League Points) and sends updates to a Discord channel.

## Purpose

The bot automatically checks for changes in rank and LP and notifies the Discord channel when updates occur. It also provides a daily synopsis of the player's rank and LP.

## Setup

1.  **Install Dependencies:**

    ```bash
    pip install discord.py requests python-dotenv
    ```

2.  **Environment Variables:**

    Create a `.env` file in the project directory and add the following environment variables:

    - `RIOT_API_KEY`: Your Riot Games API key. Get one at [https://developer.riotgames.com/](https://developer.riotgames.com/)
    - `SUMMONER_ID`: The summoner ID of the League of Legends player.
    - `DISCORD_TOKEN`: Your Discord bot token. Get one at [https://discord.com/developers/applications](https://discord.com/developers/applications)
    - `CHANNEL_ID`: The ID of the Discord channel to send updates to.
    - `PUUID`: The PUUID of the League of Legends player.

3.  **Run the Bot:**

    ```bash
    python main.py
    ```

## Environment Variables Explained

- `RIOT_API_KEY`: This is your personal API key from Riot Games, which allows the bot to access League of Legends data.
- `SUMMONER_ID`: This is the unique identifier for the summoner you want to track.
- `DISCORD_TOKEN`: This is the token that authenticates your bot with Discord.
- `CHANNEL_ID`: This is the ID of the Discord channel where the bot will post updates. To get the channel ID, enable developer mode in Discord, then right-click the channel and select "Copy ID".
- `PUUID`: This is the player's unique identifier, used to fetch the summoner name.

## Usage

The bot will automatically check the rank and LP of the specified summoner and send updates to the Discord channel whenever there is a change. It will also send a daily synopsis at 8 AM UTC.

## Data Storage

The bot stores the previous rank and LP data in a file named `last_data.json`. This file is used to detect changes in rank and LP.

## Troubleshooting

- Make sure all environment variables are set correctly in the `.env` file.
- Ensure that the bot has the necessary permissions to send messages to the Discord channel.
- Check the console output for any error messages.
