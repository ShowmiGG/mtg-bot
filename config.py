import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!mtg')

# Game settings
STARTING_LIFE = 40  # Commander starting life total
MAX_PLAYERS = 4
MIN_PLAYERS = 2

# Scryfall API
SCRYFALL_API_BASE = 'https://api.scryfall.com'
SCRYFALL_CARD_SEARCH = f'{SCRYFALL_API_BASE}/cards/named'

# Embed colors
COLOR_PRIMARY = 0x7289DA
COLOR_SUCCESS = 0x43B581
COLOR_ERROR = 0xF04747
COLOR_WARNING = 0xFAA61A
