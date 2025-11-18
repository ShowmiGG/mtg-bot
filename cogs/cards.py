import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import config


class Cards(commands.Cog):
    """Commands for searching and displaying MTG cards"""

    def __init__(self, bot):
        self.bot = bot
        self.session = None

    async def cog_load(self):
        """Create aiohttp session when cog loads"""
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        """Close aiohttp session when cog unloads"""
        if self.session:
            await self.session.close()

    async def search_card(self, card_name: str):
        """Search for a card using Scryfall API"""
        params = {
            'fuzzy': card_name
        }

        try:
            async with self.session.get(config.SCRYFALL_CARD_SEARCH, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    return None
        except Exception as e:
            print(f"Error searching for card: {e}")
            return None

    def get_mana_cost_emoji(self, mana_cost: str) -> str:
        """Convert mana cost to a readable format"""
        if not mana_cost:
            return "No mana cost"

        # Simple text replacement for common symbols
        mana_cost = mana_cost.replace('{', '').replace('}', ' ').strip()
        return mana_cost

    def get_color_for_card(self, colors) -> int:
        """Get embed color based on card colors"""
        if not colors:
            return 0x9E9E9E  # Colorless - Gray

        # Single color
        color_map = {
            'W': 0xF0F2C0,  # White
            'U': 0x0E68AB,  # Blue
            'B': 0x150B00,  # Black
            'R': 0xD3202A,  # Red
            'G': 0x00733E,  # Green
        }

        if len(colors) == 1:
            return color_map.get(colors[0], 0x9E9E9E)

        # Multicolor
        return 0xF9E084

    @commands.command(name='card', aliases=['c'])
    async def search_card_command(self, ctx, *, card_name: str):
        """
        Search for an MTG card
        Example: !mtg card Sol Ring
        """
        async with ctx.typing():
            card_data = await self.search_card(card_name)

            if not card_data:
                await ctx.send(f'Card not found: **{card_name}**')
                return

            # Create embed
            embed = discord.Embed(
                title=card_data.get('name', 'Unknown'),
                url=card_data.get('scryfall_uri', ''),
                description=card_data.get('type_line', ''),
                color=self.get_color_for_card(card_data.get('colors', []))
            )

            # Mana cost
            if 'mana_cost' in card_data:
                embed.add_field(
                    name="Mana Cost",
                    value=self.get_mana_cost_emoji(card_data['mana_cost']),
                    inline=True
                )

            # Oracle text
            if 'oracle_text' in card_data:
                oracle_text = card_data['oracle_text']
                # Limit oracle text length for embed
                if len(oracle_text) > 1024:
                    oracle_text = oracle_text[:1021] + "..."
                embed.add_field(
                    name="Text",
                    value=oracle_text,
                    inline=False
                )

            # Power/Toughness for creatures
            if 'power' in card_data and 'toughness' in card_data:
                embed.add_field(
                    name="P/T",
                    value=f"{card_data['power']}/{card_data['toughness']}",
                    inline=True
                )

            # Loyalty for planeswalkers
            if 'loyalty' in card_data:
                embed.add_field(
                    name="Loyalty",
                    value=card_data['loyalty'],
                    inline=True
                )

            # Set info
            if 'set_name' in card_data:
                embed.set_footer(
                    text=f"{card_data['set_name']} • {card_data.get('rarity', 'Unknown').capitalize()}"
                )

            # Card image
            if 'image_uris' in card_data:
                embed.set_image(url=card_data['image_uris'].get('normal', ''))
            elif 'card_faces' in card_data and card_data['card_faces']:
                # Double-faced cards
                if 'image_uris' in card_data['card_faces'][0]:
                    embed.set_image(url=card_data['card_faces'][0]['image_uris'].get('normal', ''))

            await ctx.send(embed=embed)

    @commands.command(name='price')
    async def card_price(self, ctx, *, card_name: str):
        """
        Get the price of a card
        Example: !mtg price Mana Crypt
        """
        async with ctx.typing():
            card_data = await self.search_card(card_name)

            if not card_data:
                await ctx.send(f'Card not found: **{card_name}**')
                return

            prices = card_data.get('prices', {})

            embed = discord.Embed(
                title=f"{card_data.get('name', 'Unknown')} - Prices",
                url=card_data.get('scryfall_uri', ''),
                color=config.COLOR_PRIMARY
            )

            # USD prices
            if prices.get('usd'):
                embed.add_field(name="USD", value=f"${prices['usd']}", inline=True)
            if prices.get('usd_foil'):
                embed.add_field(name="USD Foil", value=f"${prices['usd_foil']}", inline=True)

            # EUR prices
            if prices.get('eur'):
                embed.add_field(name="EUR", value=f"€{prices['eur']}", inline=True)

            if not any(prices.values()):
                embed.description = "No price data available for this card."

            # Card thumbnail
            if 'image_uris' in card_data:
                embed.set_thumbnail(url=card_data['image_uris'].get('small', ''))

            await ctx.send(embed=embed)

    @commands.command(name='random')
    async def random_card(self, ctx):
        """Get a random MTG card"""
        async with ctx.typing():
            try:
                url = f"{config.SCRYFALL_API_BASE}/cards/random"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        card_data = await response.json()
                        # Reuse the card display logic
                        await ctx.invoke(self.bot.get_command('card'), card_name=card_data['name'])
                    else:
                        await ctx.send("Failed to get a random card.")
            except Exception as e:
                await ctx.send(f"Error: {str(e)}")


    # Slash Commands
    @app_commands.command(name="card", description="Search for an MTG card")
    @app_commands.describe(name="Card name to search for")
    async def slash_card(self, interaction: discord.Interaction, name: str):
        """Search for a card via slash command"""
        await interaction.response.defer()  # Card search might take a moment

        card_data = await self.search_card(name)

        if not card_data:
            await interaction.followup.send(f'Card not found: **{name}**')
            return

        # Create embed (same as prefix command)
        embed = discord.Embed(
            title=card_data.get('name', 'Unknown'),
            url=card_data.get('scryfall_uri', ''),
            description=card_data.get('type_line', ''),
            color=self.get_color_for_card(card_data.get('colors', []))
        )

        if 'mana_cost' in card_data:
            embed.add_field(
                name="Mana Cost",
                value=self.get_mana_cost_emoji(card_data['mana_cost']),
                inline=True
            )

        if 'oracle_text' in card_data:
            oracle_text = card_data['oracle_text']
            if len(oracle_text) > 1024:
                oracle_text = oracle_text[:1021] + "..."
            embed.add_field(name="Text", value=oracle_text, inline=False)

        if 'power' in card_data and 'toughness' in card_data:
            embed.add_field(
                name="P/T",
                value=f"{card_data['power']}/{card_data['toughness']}",
                inline=True
            )

        if 'loyalty' in card_data:
            embed.add_field(name="Loyalty", value=card_data['loyalty'], inline=True)

        if 'set_name' in card_data:
            embed.set_footer(
                text=f"{card_data['set_name']} • {card_data.get('rarity', 'Unknown').capitalize()}"
            )

        if 'image_uris' in card_data:
            embed.set_image(url=card_data['image_uris'].get('normal', ''))
        elif 'card_faces' in card_data and card_data['card_faces']:
            if 'image_uris' in card_data['card_faces'][0]:
                embed.set_image(url=card_data['card_faces'][0]['image_uris'].get('normal', ''))

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="roll", description="Roll dice")
    @app_commands.describe(dice="Dice notation (e.g., d20, 2d6, 4d8)")
    async def slash_roll(self, interaction: discord.Interaction, dice: str = 'd20'):
        """Roll dice via slash command"""
        import random
        import re

        match = re.match(r'^(\d+)?d(\d+)$', dice.lower())

        if not match:
            await interaction.response.send_message('Invalid dice format. Use format like: d20, 2d6, 4d8')
            return

        num_dice = int(match.group(1)) if match.group(1) else 1
        die_size = int(match.group(2))

        if num_dice > 100:
            await interaction.response.send_message('Maximum 100 dice at once!')
            return

        if die_size > 1000:
            await interaction.response.send_message('Maximum die size is 1000!')
            return

        rolls = [random.randint(1, die_size) for _ in range(num_dice)]
        total = sum(rolls)

        embed = discord.Embed(title=f"🎲 Rolling {dice}", color=config.COLOR_PRIMARY)

        if num_dice == 1:
            embed.description = f"**Result: {total}**"
        else:
            if num_dice <= 20:
                rolls_str = ', '.join(map(str, rolls))
                embed.add_field(name="Rolls", value=rolls_str, inline=False)

            embed.add_field(name="Total", value=f"**{total}**", inline=False)

        embed.set_footer(text=f"Rolled by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Cards(bot))
