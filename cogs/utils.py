import discord
from discord.ext import commands
import random
import re
import config
from models import CommanderGame


class Utils(commands.Cog):
    """Utility commands for dice, coins, counters, etc."""

    def __init__(self, bot):
        self.bot = bot

    def get_game(self, channel_id: int) -> CommanderGame:
        """Get game from the Game cog"""
        game_cog = self.bot.get_cog('Game')
        if game_cog:
            return game_cog.get_game(channel_id)
        return None

    @commands.command(name='roll')
    async def roll_dice(self, ctx, dice: str = 'd20'):
        """
        Roll dice
        Examples: !mtg roll d20, !mtg roll 2d6, !mtg roll 4d6
        """
        # Parse dice notation (e.g., 2d6, d20)
        match = re.match(r'^(\d+)?d(\d+)$', dice.lower())

        if not match:
            await ctx.send('Invalid dice format. Use format like: d20, 2d6, 4d8')
            return

        num_dice = int(match.group(1)) if match.group(1) else 1
        die_size = int(match.group(2))

        if num_dice > 100:
            await ctx.send('Maximum 100 dice at once!')
            return

        if die_size > 1000:
            await ctx.send('Maximum die size is 1000!')
            return

        # Roll the dice
        rolls = [random.randint(1, die_size) for _ in range(num_dice)]
        total = sum(rolls)

        embed = discord.Embed(
            title=f"🎲 Rolling {dice}",
            color=config.COLOR_PRIMARY
        )

        if num_dice == 1:
            embed.description = f"**Result: {total}**"
        else:
            # Show individual rolls if not too many
            if num_dice <= 20:
                rolls_str = ', '.join(map(str, rolls))
                embed.add_field(name="Rolls", value=rolls_str, inline=False)

            embed.add_field(name="Total", value=f"**{total}**", inline=False)

        embed.set_footer(text=f"Rolled by {ctx.author.display_name}")

        await ctx.send(embed=embed)

    @commands.command(name='flip')
    async def flip_coin(self, ctx, times: int = 1):
        """
        Flip a coin
        Example: !mtg flip, !mtg flip 3
        """
        if times > 100:
            await ctx.send('Maximum 100 flips at once!')
            return

        if times < 1:
            times = 1

        results = [random.choice(['Heads', 'Tails']) for _ in range(times)]

        embed = discord.Embed(
            title=f"🪙 Flipping {times} coin{'s' if times > 1 else ''}",
            color=config.COLOR_PRIMARY
        )

        if times == 1:
            embed.description = f"**{results[0]}!**"
        else:
            heads = results.count('Heads')
            tails = results.count('Tails')

            embed.add_field(name="Heads", value=str(heads), inline=True)
            embed.add_field(name="Tails", value=str(tails), inline=True)

            if times <= 20:
                results_str = ', '.join(results)
                embed.add_field(name="Results", value=results_str, inline=False)

        embed.set_footer(text=f"Flipped by {ctx.author.display_name}")

        await ctx.send(embed=embed)

    @commands.command(name='counter')
    async def manage_counter(self, ctx, counter_name: str, amount: int = 1):
        """
        Add counters to yourself (poison, energy, experience, etc.)
        Examples: !mtg counter poison 3, !mtg counter energy 5
        """
        game = self.get_game(ctx.channel.id)

        if not game:
            await ctx.send('No active game!')
            return

        player = game.get_player(ctx.author.id)

        if not player:
            await ctx.send('You are not in an active game!')
            return

        counter_name = counter_name.lower()
        player.add_counter(counter_name, amount)
        new_count = player.get_counter(counter_name)

        embed = discord.Embed(
            title=f"Counter Updated",
            description=f"{ctx.author.display_name} now has **{new_count}** {counter_name} counter{'s' if new_count != 1 else ''}",
            color=config.COLOR_PRIMARY
        )

        # Special warning for poison
        if counter_name == 'poison' and new_count >= 10:
            embed.add_field(
                name="⚠️ Warning",
                value="You have 10 or more poison counters!",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='reset')
    async def reset_counters(self, ctx, counter_name: str = None):
        """
        Reset counters to 0
        Example: !mtg reset poison, !mtg reset (resets all)
        """
        game = self.get_game(ctx.channel.id)

        if not game:
            await ctx.send('No active game!')
            return

        player = game.get_player(ctx.author.id)

        if not player:
            await ctx.send('You are not in an active game!')
            return

        if counter_name:
            counter_name = counter_name.lower()
            if counter_name in player.counters:
                player.counters[counter_name] = 0
                await ctx.send(f"Reset {counter_name} counters for {ctx.author.display_name}")
            else:
                await ctx.send(f"You don't have any {counter_name} counters.")
        else:
            player.counters.clear()
            await ctx.send(f"Reset all counters for {ctx.author.display_name}")

    @commands.command(name='mulligan')
    async def mulligan(self, ctx, cards: int = 7):
        """
        Simulate a mulligan (draw new hand)
        Example: !mtg mulligan 6
        """
        if cards < 0 or cards > 7:
            await ctx.send('Hand size must be between 0 and 7.')
            return

        embed = discord.Embed(
            title="🔄 Mulligan",
            description=f"{ctx.author.display_name} mulliganed to **{cards}** cards",
            color=config.COLOR_WARNING
        )

        if cards < 7:
            embed.set_footer(text="Don't forget to scry 1 if you mulliganed! (Free mulligan if first)")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utils(bot))
