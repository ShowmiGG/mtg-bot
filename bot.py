import discord
from discord import app_commands
from discord.ext import commands
import config
import sys

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix=config.COMMAND_PREFIX + ' ',
    intents=intents,
    help_command=None
)

# Command tree for slash commands
tree = bot.tree


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print(f'Command prefix: {config.COMMAND_PREFIX}')
    print('Bot is ready!')
    print('------')
    sys.stdout.flush()


@bot.event
async def on_command_error(ctx, error):
    """Global error handler with helpful hints"""
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Command Not Found",
            description=f"That command doesn't exist. Use `{config.COMMAND_PREFIX} help` to see all available commands.",
            color=config.COLOR_ERROR
        )
        embed.add_field(
            name="💡 Quick Tip",
            value=f"Common commands:\n`{config.COMMAND_PREFIX} start` - Start a game\n`{config.COMMAND_PREFIX} card <name>` - Search cards\n`{config.COMMAND_PREFIX} roll d20` - Roll dice",
            inline=False
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        command_name = ctx.command.name if ctx.command else "command"
        embed = discord.Embed(
            title="⚠️ Missing Argument",
            description=f"This command requires more information.",
            color=config.COLOR_WARNING
        )
        embed.add_field(
            name="Missing",
            value=f"`{error.param.name}`",
            inline=False
        )
        embed.add_field(
            name="💡 Hint",
            value=f"Use `{config.COMMAND_PREFIX} help` to see command examples and usage.",
            inline=False
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="⚠️ Invalid Argument",
            description="The argument you provided isn't valid for this command.",
            color=config.COLOR_WARNING
        )
        embed.add_field(
            name="💡 Hint",
            value=f"Check `{config.COMMAND_PREFIX} help` for proper command format and examples.",
            inline=False
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="❌ Player Not Found",
            description="I couldn't find that player. Make sure you're mentioning them correctly.",
            color=config.COLOR_ERROR
        )
        embed.add_field(
            name="💡 Hint",
            value="Use @mentions like: `!mtg cmdr @PlayerName 3`",
            inline=False
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Something went wrong: {str(error)}",
            color=config.COLOR_ERROR
        )
        await ctx.send(embed=embed)
        print(f'Error: {error}', file=sys.stderr)
        sys.stdout.flush()


@bot.command(name='help', aliases=['h', 'commands'])
async def help_command(ctx, category: str = None):
    """Display help information"""

    if category and category.lower() == 'game':
        embed = discord.Embed(
            title="Game Management Commands",
            description="Commands for starting and managing Commander games",
            color=config.COLOR_PRIMARY
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} start",
            value="Start a new Commander game in this channel.\n**Example:** `!mtg start`",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} join",
            value="Join an existing game waiting for players.\n**Example:** `!mtg join`",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} begin",
            value="Begin the game once all players have joined.\n**Example:** `!mtg begin`",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} status",
            value="View current game state, life totals, and damage.\n**Example:** `!mtg status`",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} leave",
            value="Leave the current game.\n**Example:** `!mtg leave`",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} end",
            value="End the current game (players only).\n**Example:** `!mtg end`",
            inline=False
        )

    elif category and category.lower() == 'life':
        embed = discord.Embed(
            title="Life & Damage Commands",
            description="Commands for tracking life and commander damage",
            color=config.COLOR_PRIMARY
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} life <amount>",
            value="Set your life to a specific amount.\n**Example:** `!mtg life 35`",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} life +<amount>",
            value="Gain life (add to current total).\n**Example:** `!mtg life +5`",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} life -<amount>",
            value="Lose life (subtract from current total).\n**Example:** `!mtg life -7`",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} cmdr @player <amount>",
            value="Deal commander damage to another player.\n**Example:** `!mtg cmdr @Alice 5`\n**Hint:** Game ends when a player takes 21 commander damage from one opponent!",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} counter <name> <amount>",
            value="Add counters (poison, energy, experience, etc.).\n**Examples:**\n`!mtg counter poison 3`\n`!mtg counter energy 5`\n**Hint:** 10 poison counters = elimination!",
            inline=False
        )

    elif category and category.lower() in ['cards', 'card']:
        embed = discord.Embed(
            title="Card Search Commands",
            description="Commands for searching MTG cards",
            color=config.COLOR_PRIMARY
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} card <name>",
            value="Search for a card by name. Shows image, text, and details.\n**Examples:**\n`!mtg card Sol Ring`\n`!mtg card Mana Crypt`\n`!mtg cCommanderName` (alias)",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} price <name>",
            value="Get current market prices for a card.\n**Example:** `!mtg price Mana Crypt`",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} random",
            value="Get a random MTG card.\n**Example:** `!mtg random`",
            inline=False
        )

    elif category and category.lower() in ['utils', 'utility', 'dice']:
        embed = discord.Embed(
            title="Utility Commands",
            description="Helpful utility commands for gameplay",
            color=config.COLOR_PRIMARY
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} roll <dice>",
            value="Roll dice using standard notation.\n**Examples:**\n`!mtg roll d20` (single d20)\n`!mtg roll 2d6` (two six-sided dice)\n`!mtg roll 4d6` (four six-sided dice)",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} flip [times]",
            value="Flip a coin (or multiple coins).\n**Examples:**\n`!mtg flip` (single flip)\n`!mtg flip 3` (flip 3 coins)",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} mulligan [cards]",
            value="Track mulligans (defaults to 7 cards).\n**Examples:**\n`!mtg mulligan 6`\n`!mtg mulligan 5`",
            inline=False
        )
        embed.add_field(
            name=f"{config.COMMAND_PREFIX} reset [counter]",
            value="Reset counters to 0.\n**Examples:**\n`!mtg reset poison`\n`!mtg reset` (resets all)",
            inline=False
        )

    else:
        # Main help menu
        embed = discord.Embed(
            title="🎴 MTG Commander Bot - Help",
            description=f"Companion bot for playing Commander\n\n**Quick Start:**\n1. `{config.COMMAND_PREFIX} start` - Start a game\n2. Players use `{config.COMMAND_PREFIX} join`\n3. `{config.COMMAND_PREFIX} begin` - Begin playing!\n\n**Get detailed help:** `{config.COMMAND_PREFIX} help <category>`",
            color=config.COLOR_PRIMARY
        )

        embed.add_field(
            name="📋 Game Management",
            value=f"`{config.COMMAND_PREFIX} help game` - Start, join, and manage games",
            inline=False
        )

        embed.add_field(
            name="❤️ Life & Damage",
            value=f"`{config.COMMAND_PREFIX} help life` - Track life totals and commander damage",
            inline=False
        )

        embed.add_field(
            name="🃏 Card Search",
            value=f"`{config.COMMAND_PREFIX} help cards` - Search cards and view prices",
            inline=False
        )

        embed.add_field(
            name="🎲 Utilities",
            value=f"`{config.COMMAND_PREFIX} help utils` - Dice, coins, counters, mulligans",
            inline=False
        )

        embed.add_field(
            name="🔧 Other Commands",
            value=f"`{config.COMMAND_PREFIX} ping` - Check bot latency",
            inline=False
        )

        embed.set_footer(text=f"Tip: Use '{config.COMMAND_PREFIX} help <category>' for detailed examples!")

    await ctx.send(embed=embed)


@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! Latency: {latency}ms')


@bot.command(name='sync')
@commands.is_owner()
async def sync(ctx):
    """Sync slash commands (Owner only)"""
    try:
        synced = await bot.tree.sync()
        await ctx.send(f'Synced {len(synced)} slash commands!')
        print(f'Synced {len(synced)} slash commands')
        sys.stdout.flush()
    except Exception as e:
        await ctx.send(f'Failed to sync: {e}')
        print(f'Sync error: {e}', file=sys.stderr)
        sys.stdout.flush()


# Slash Commands
@tree.command(name="ping", description="Check bot latency")
async def slash_ping(interaction: discord.Interaction):
    """Check bot latency via slash command"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f'🏓 Pong! Latency: {latency}ms')


async def load_extensions():
    """Load all cog extensions"""
    extensions = [
        'cogs.game',
        'cogs.cards',
        'cogs.utils'
    ]

    for extension in extensions:
        try:
            await bot.load_extension(extension)
            print(f'Loaded extension: {extension}')
            sys.stdout.flush()
        except Exception as e:
            print(f'Failed to load extension {extension}: {e}')
            sys.stdout.flush()


async def main():
    """Main bot startup"""
    print('Starting MTG Commander Bot...')
    sys.stdout.flush()

    async with bot:
        await load_extensions()

        if not config.DISCORD_TOKEN:
            print('Error: DISCORD_TOKEN not found in .env file')
            print('Please copy .env.example to .env and add your bot token')
            return

        print('Connecting to Discord...')
        sys.stdout.flush()
        await bot.start(config.DISCORD_TOKEN)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
