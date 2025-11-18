# MTG Commander Discord Bot

A Discord bot companion for playing Magic: The Gathering Commander format.

## Features

- **Life Tracking**: Track life totals for up to 4 players
- **Commander Damage**: Monitor commander damage between players
- **Card Search**: Search and display MTG cards using Scryfall API
- **Dice & Utilities**: Roll dice, flip coins, manage counters
- **Game Sessions**: Create and manage Commander game lobbies

## Setup

1. **Install Python 3.9+**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a Discord Bot**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to "Bot" section and create a bot
   - Copy the bot token

4. **Configure the bot**:
   - Copy `.env.example` to `.env`
   - Add your Discord bot token to `.env`

5. **Invite the bot to your server**:
   - Go to OAuth2 > URL Generator
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Send Messages`, `Embed Links`, `Read Message History`
   - Use the generated URL to invite the bot

6. **Run the bot**:
   ```bash
   python bot.py
   ```

## Commands

### 📖 Getting Help

The bot has an interactive help system with detailed examples!

- `!mtg help` - Main help menu
- `!mtg help game` - Game management commands with examples
- `!mtg help life` - Life and damage tracking commands
- `!mtg help cards` - Card search commands
- `!mtg help utils` - Utility commands (dice, coins, etc.)

**Aliases:** You can also use `!mtg h` or `!mtg commands`

### ⚡ Slash Commands

The bot supports modern Discord slash commands (`/`) with autocomplete and hints!

**After inviting the bot, sync slash commands once:**
```
!mtg sync
```

Then you can use slash commands like:
- `/start` - Start a game with autocomplete
- `/join` - Join with hints
- `/life +5` - Life changes with parameter descriptions
- `/card Sol Ring` - Card search with autocomplete
- `/roll d20` - Dice rolling
- `/status` - View game state

**Benefits of slash commands:**
- Auto-complete suggestions
- Parameter descriptions and hints
- Better mobile experience
- Cleaner command discovery

### 🎮 Quick Command Reference

#### Game Management
- `!mtg start` - Start a new Commander game
- `!mtg join` - Join an active game
- `!mtg begin` - Begin the game once all players joined
- `!mtg status` - Show current game state
- `!mtg leave` - Leave the current game
- `!mtg end` - End the current game

#### Life & Damage
- `!mtg life 35` - Set your life total
- `!mtg life +5` - Gain life
- `!mtg life -7` - Lose life
- `!mtg cmdr @player 3` - Deal commander damage to a player
- `!mtg counter poison 2` - Add poison counters (or energy, experience, etc.)
- `!mtg reset poison` - Reset specific counter to 0

#### Card Search
- `!mtg card Sol Ring` - Search for a card and display its details
- `!mtg price Mana Crypt` - Get current market prices
- `!mtg random` - Get a random card

#### Utilities
- `!mtg roll d20` - Roll a d20
- `!mtg roll 2d6` - Roll 2 six-sided dice
- `!mtg flip` - Flip a coin
- `!mtg flip 3` - Flip 3 coins
- `!mtg mulligan 6` - Track a mulligan to 6 cards

## Deployment

### Deploy to Render

This bot is ready to deploy to [Render](https://render.com) for 24/7 uptime!

**Quick Deploy:**
1. Push this code to GitHub
2. Create a Render account
3. Connect your repository
4. Add your `DISCORD_TOKEN` as an environment variable
5. Deploy!

📚 **[Full Deployment Guide](DEPLOYMENT.md)** - Step-by-step instructions

**Note:** Render's free tier may spin down after inactivity. For always-on bot service, consider the paid plan ($7/month) or alternative hosting (Railway, fly.io, VPS).

## Project Structure

```
MTG-Bot/
├── bot.py              # Main bot with slash command support
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── models/             # Game data models
│   ├── game.py         # Player and game logic
│   └── __init__.py
└── cogs/               # Command modules
    ├── game.py         # Game management commands
    ├── cards.py        # Card search (Scryfall API)
    └── utils.py        # Utilities (dice, coins, etc.)
```

## License

MIT
