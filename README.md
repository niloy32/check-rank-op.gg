# League of Legends Rank Tracker Discord Bot

## What This Repository Does

This repository contains an automated Discord bot that continuously monitors a League of Legends player's ranked statistics and provides real-time notifications. Here's what it does:

### 🎮 **Core Functionality**
- **Tracks Rank Changes**: Monitors your League of Legends rank (Bronze, Silver, Gold, etc.) and division changes
- **LP Monitoring**: Tracks League Points (LP) gains and losses after each ranked game
- **Win/Loss Statistics**: Keeps track of total wins and losses for the season
- **Hot Streak Detection**: Identifies and celebrates when you're on a winning streak
- **Daily Summaries**: Provides a daily synopsis of your current rank status at 8 AM UTC

### 🤖 **Automated Notifications**
The bot sends Discord messages when:
- Your rank changes (promotions or demotions)
- Your LP increases or decreases after games
- You're on a hot streak (special celebration message)
- Daily status updates (configurable time)

### ⚡ **Automated Execution**
- Runs automatically every hour via GitHub Actions
- No need for a dedicated server - uses GitHub's infrastructure
- Automatically updates tracking data and commits changes to the repository

### 💬 **Discord Integration**
- Sends formatted messages to your specified Discord channel
- Easy-to-read rank updates with visual indicators (🔼🔽 for LP changes)
- Special hot streak notifications with fire emojis 🔥

## How It Works

### 🔄 **Automated Workflow**
1. **GitHub Actions** runs the bot every hour automatically
2. The bot fetches current rank data from **Riot Games API**
3. Compares with previously stored data in `last_data.json`
4. If changes are detected, sends notifications to your **Discord channel**
5. Updates the data file and commits changes back to the repository

### 📊 **Data Tracking**
- Current rank and division (e.g., "Gold III")
- League Points (LP)
- Total wins and losses
- Hot streak status
- Player summoner name and tag

## Setup and Installation

1.  **Install Dependencies:**

    ```bash
    pip install discord.py requests python-dotenv
    ```

2.  **GitHub Repository Setup (for Automation):**
    
    Fork this repository and set up the following **repository secrets** in GitHub:
    - Go to your repository → Settings → Secrets and Variables → Actions
    - Add the following secrets:
      - `RIOT_API_KEY`: Your Riot Games API key
      - `SUMMONER_ID`: The summoner ID of the League of Legends player
      - `DISCORD_TOKEN`: Your Discord bot token
      - `CHANNEL_ID`: The ID of the Discord channel to send updates to
      - `PUUID`: The PUUID of the League of Legends player

3.  **Local Development (Optional):**

    If you want to run the bot locally for testing:

    Create a `.env` file in the project directory with the same environment variables:

    ```env
    RIOT_API_KEY=your_riot_api_key_here
    SUMMONER_ID=your_summoner_id_here
    DISCORD_TOKEN=your_discord_bot_token_here
    CHANNEL_ID=your_channel_id_here
    PUUID=your_puuid_here
    ```

4.  **Run the Bot:**

    For local testing:
    ```bash
    python main.py
    ```
    
    For production: The bot runs automatically via GitHub Actions every hour.

## Configuration Guide

### 🔑 **Required API Keys and IDs**

- **`RIOT_API_KEY`**: Get your personal API key from [Riot Developer Portal](https://developer.riotgames.com/)
  - Sign in with your Riot account
  - Generate a personal API key (valid for 24 hours for development)
  - For production, apply for a production API key

- **`DISCORD_TOKEN`**: Create a Discord bot at [Discord Developer Portal](https://discord.com/developers/applications)
  - Create a new application
  - Go to "Bot" section and create a bot
  - Copy the bot token
  - Invite the bot to your server with "Send Messages" permission

- **`CHANNEL_ID`**: Get your Discord channel ID
  - Enable Developer Mode in Discord (User Settings → App Settings → Advanced → Developer Mode)
  - Right-click on your channel and select "Copy ID"

- **`SUMMONER_ID`** and **`PUUID`**: Get these from Riot API or online tools
  - Use Riot API endpoints or tools like op.gg to find your summoner data
  - SUMMONER_ID is for the specific region's League API
  - PUUID is the global player identifier

### 🌍 **Regional Configuration**
The bot is currently configured for Singapore/Asia regions. If you need different regions, update these URLs in `main.py`:
- `BASE_URL = 'https://sg2.api.riotgames.com'` (for League data)
- `SUMMONER_ENDPOINT` uses `https://asia.api.riotgames.com` (for account data)

## Features in Action

### 📈 **Rank Change Notifications**
```
**Rank Update for Summoner:** PlayerName#TAG
**Rank:** Gold II (from Gold III to Gold II)
**LP:** 45 (🔼 +18 LP)
**Wins:** 85
**Losses:** 96
```

### 🔥 **Hot Streak Celebrations**
```
**Rank Update for Summoner:** PlayerName#TAG
**Rank:** Gold II
**LP:** 63 (🔼 +18 LP)
**Wins:** 87
**Losses:** 96
🔥 King Araaf is currently on a hot streak! 🔥
```

### 📅 **Daily Synopsis (8 AM UTC)**
```
**Daily Synopsis for PlayerName#TAG:**
**Rank:** Gold II
**LP:** 63
**Wins:** 87
**Losses:** 96
```

## Automation Details

- **Frequency**: Runs every hour via GitHub Actions
- **Data Persistence**: Stores previous rank data in `last_data.json`
- **Change Detection**: Only sends notifications when rank or LP actually changes
- **Auto-commit**: Automatically commits data updates back to the repository

## File Structure

```
check-rank-op.gg/
├── main.py              # Core Discord bot application
├── last_data.json       # Stores previous rank data for comparison
├── README.md           # This documentation
├── .github/
│   └── workflows/
│       └── main.yml    # GitHub Actions automation workflow
└── .gitignore         # Git ignore file
```

## Troubleshooting

### 🔧 **Common Issues**

- **Bot not sending messages**: 
  - Verify all GitHub repository secrets are set correctly
  - Ensure Discord bot has "Send Messages" permission in the target channel
  - Check that CHANNEL_ID is correct (numeric value)

- **API errors**:
  - Verify RIOT_API_KEY is valid and not expired
  - Ensure SUMMONER_ID and PUUID are correct for the player
  - Check if the player has played ranked games this season

- **GitHub Actions failing**:
  - Check the Actions tab in your repository for error details
  - Verify all secrets are properly configured
  - Ensure the workflow has write permissions

### 📊 **Monitoring**
- Check GitHub Actions logs for detailed error messages
- Monitor the commits to see when `last_data.json` was last updated
- Test locally first before relying on automation

## Contributing

Feel free to fork this repository and customize it for your needs! You can:
- Modify the message format in `main.py`
- Change the checking frequency in `.github/workflows/main.yml`
- Add support for multiple players
- Enhance notifications with more detailed statistics
