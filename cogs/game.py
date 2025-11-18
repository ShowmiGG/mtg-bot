import discord
from discord import app_commands
from discord.ext import commands
from typing import Dict
import config
from models import CommanderGame


class Game(commands.Cog):
    """Commands for managing Commander games"""

    def __init__(self, bot):
        self.bot = bot
        self.games: Dict[int, CommanderGame] = {}  # {channel_id: CommanderGame}

    def get_game(self, channel_id: int) -> CommanderGame:
        """Get or create a game for a channel"""
        if channel_id not in self.games:
            self.games[channel_id] = CommanderGame(channel_id)
        return self.games[channel_id]

    @commands.command(name='start')
    async def start_game(self, ctx):
        """Start a new Commander game"""
        game = self.get_game(ctx.channel.id)

        if game.active:
            await ctx.send('A game is already in progress in this channel!')
            return

        # Reset game if it was previously played
        self.games[ctx.channel.id] = CommanderGame(ctx.channel.id)
        game = self.games[ctx.channel.id]

        # Add the user who started the game
        game.add_player(ctx.author.id, ctx.author.display_name)

        embed = discord.Embed(
            title="Commander Game Started!",
            description=f"{ctx.author.display_name} started a new game.",
            color=config.COLOR_SUCCESS
        )
        embed.add_field(
            name="Players",
            value=f"1. {ctx.author.display_name}",
            inline=False
        )
        embed.add_field(
            name="How to Join",
            value=f"Use `{config.COMMAND_PREFIX} join` to join the game!",
            inline=False
        )
        embed.set_footer(text=f"Starting life: {config.STARTING_LIFE} | Players: 1/{config.MAX_PLAYERS}")

        await ctx.send(embed=embed)

    @commands.command(name='join')
    async def join_game(self, ctx):
        """Join an active game"""
        game = self.get_game(ctx.channel.id)

        if game.started and game.active:
            await ctx.send('The game has already started!')
            return

        if not game.players:
            await ctx.send(f'No game in progress. Use `{config.COMMAND_PREFIX} start` to start a new game.')
            return

        if game.add_player(ctx.author.id, ctx.author.display_name):
            player_list = '\n'.join([f"{i+1}. {p.username}" for i, p in enumerate(game.players.values())])

            embed = discord.Embed(
                title="Player Joined!",
                description=f"{ctx.author.display_name} joined the game.",
                color=config.COLOR_SUCCESS
            )
            embed.add_field(name="Current Players", value=player_list, inline=False)
            embed.set_footer(text=f"Players: {len(game.players)}/{config.MAX_PLAYERS}")

            await ctx.send(embed=embed)

            # Auto-start if we have enough players
            if len(game.players) >= config.MIN_PLAYERS and not game.started:
                embed = discord.Embed(
                    title="Ready to Begin!",
                    description=f"Use `{config.COMMAND_PREFIX} begin` to start the game, or wait for more players.",
                    color=config.COLOR_WARNING
                )
                await ctx.send(embed=embed)
        else:
            if ctx.author.id in game.players:
                await ctx.send('You are already in this game!')
            else:
                await ctx.send(f'Game is full! (Max {config.MAX_PLAYERS} players)')

    @commands.command(name='begin')
    async def begin_game(self, ctx):
        """Begin the game once all players have joined"""
        game = self.get_game(ctx.channel.id)

        if not game.players:
            await ctx.send(f'No game to begin. Use `{config.COMMAND_PREFIX} start` first.')
            return

        if game.started:
            await ctx.send('Game has already begun!')
            return

        if ctx.author.id not in game.players:
            await ctx.send('Only players in the game can start it!')
            return

        if game.start_game():
            player_list = '\n'.join([f"{p.username}: {p.life} life" for p in game.players.values()])

            embed = discord.Embed(
                title="Game Begin!",
                description="The Commander game has started!",
                color=config.COLOR_SUCCESS
            )
            embed.add_field(name="Players", value=player_list, inline=False)
            embed.add_field(
                name="Commands",
                value=(
                    f"`{config.COMMAND_PREFIX} status` - View game state\n"
                    f"`{config.COMMAND_PREFIX} life [+/-]amount` - Modify life\n"
                    f"`{config.COMMAND_PREFIX} cmdr @player amount` - Deal commander damage"
                ),
                inline=False
            )

            await ctx.send(embed=embed)
        else:
            await ctx.send(f'Need at least {config.MIN_PLAYERS} players to start!')

    @commands.command(name='leave')
    async def leave_game(self, ctx):
        """Leave the current game"""
        game = self.get_game(ctx.channel.id)

        if game.remove_player(ctx.author.id):
            await ctx.send(f'{ctx.author.display_name} left the game.')

            if not game.players:
                game.end_game()
                await ctx.send('Game ended - no players remaining.')
        else:
            await ctx.send('You are not in this game.')

    @commands.command(name='end')
    async def end_game(self, ctx):
        """End the current game"""
        game = self.get_game(ctx.channel.id)

        if not game.players:
            await ctx.send('No active game to end.')
            return

        if ctx.author.id not in game.players:
            await ctx.send('Only players can end the game!')
            return

        game.end_game()
        del self.games[ctx.channel.id]

        await ctx.send('Game ended.')

    @commands.command(name='status')
    async def game_status(self, ctx):
        """Show the current game status"""
        game = self.get_game(ctx.channel.id)

        if not game.players:
            await ctx.send(f'No active game. Use `{config.COMMAND_PREFIX} start` to begin!')
            return

        embed = discord.Embed(
            title="Commander Game Status",
            color=config.COLOR_PRIMARY
        )

        for player in game.players.values():
            status_lines = [f"Life: **{player.life}**"]

            # Commander damage
            if player.commander_damage:
                cmdr_dmg = [f"{game.players[pid].username}: {dmg}"
                           for pid, dmg in player.commander_damage.items()]
                status_lines.append(f"Commander Damage: {', '.join(cmdr_dmg)}")

            # Special counters
            if player.counters:
                counter_str = ', '.join([f"{name}: {count}"
                                        for name, count in player.counters.items()])
                status_lines.append(f"Counters: {counter_str}")

            # Death status
            if player.is_dead():
                status_lines.append("💀 **ELIMINATED**")

            embed.add_field(
                name=player.username,
                value='\n'.join(status_lines),
                inline=True
            )

        # Check for winner
        winner = game.check_winner()
        if winner:
            embed.add_field(
                name="🏆 Winner",
                value=f"**{winner.username}** is the last player standing!",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='life')
    async def modify_life(self, ctx, amount: str):
        """
        Modify your life total
        Examples: !mtg life 35, !mtg life +5, !mtg life -3
        """
        game = self.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)

        if not player:
            await ctx.send('You are not in an active game!')
            return

        try:
            if amount.startswith('+') or amount.startswith('-'):
                # Relative change
                change = int(amount)
                player.modify_life(change)
                action = "gained" if change > 0 else "lost"
                await ctx.send(f'{ctx.author.display_name} {action} {abs(change)} life. Now at **{player.life}** life.')
            else:
                # Absolute set
                new_life = int(amount)
                player.set_life(new_life)
                await ctx.send(f'{ctx.author.display_name} set life to **{player.life}**.')

            # Check if player died
            if player.is_dead():
                await ctx.send(f'💀 {ctx.author.display_name} has been eliminated!')

                # Check for winner
                winner = game.check_winner()
                if winner:
                    await ctx.send(f'🏆 **{winner.username}** wins the game!')

        except ValueError:
            await ctx.send(f'Invalid amount. Use a number, +number, or -number.')

    @commands.command(name='cmdr')
    async def commander_damage(self, ctx, target: discord.Member, amount: int = 1):
        """
        Deal commander damage to another player
        Example: !mtg cmdr @PlayerName 3
        """
        game = self.get_game(ctx.channel.id)
        attacker = game.get_player(ctx.author.id)
        defender = game.get_player(target.id)

        if not attacker:
            await ctx.send('You are not in an active game!')
            return

        if not defender:
            await ctx.send(f'{target.display_name} is not in this game!')
            return

        if attacker.user_id == defender.user_id:
            await ctx.send('You cannot deal commander damage to yourself!')
            return

        defender.add_commander_damage(attacker.user_id, amount)
        total_dmg = defender.get_commander_damage(attacker.user_id)

        await ctx.send(
            f'⚔️ {ctx.author.display_name} dealt **{amount}** commander damage to {target.display_name}! '
            f'(Total: **{total_dmg}**/21)'
        )

        # Check if defender died
        if defender.is_dead():
            await ctx.send(f'💀 {target.display_name} has been eliminated!')

            # Check for winner
            winner = game.check_winner()
            if winner:
                await ctx.send(f'🏆 **{winner.username}** wins the game!')


    # Slash Commands
    @app_commands.command(name="start", description="Start a new Commander game")
    async def slash_start(self, interaction: discord.Interaction):
        """Start a new Commander game via slash command"""
        game = self.get_game(interaction.channel_id)

        if game.active:
            await interaction.response.send_message('A game is already in progress in this channel!')
            return

        # Reset game
        self.games[interaction.channel_id] = CommanderGame(interaction.channel_id)
        game = self.games[interaction.channel_id]
        game.add_player(interaction.user.id, interaction.user.display_name)

        embed = discord.Embed(
            title="Commander Game Started!",
            description=f"{interaction.user.display_name} started a new game.",
            color=config.COLOR_SUCCESS
        )
        embed.add_field(name="Players", value=f"1. {interaction.user.display_name}", inline=False)
        embed.add_field(name="How to Join", value="Use `/join` to join the game!", inline=False)
        embed.set_footer(text=f"Starting life: {config.STARTING_LIFE} | Players: 1/{config.MAX_PLAYERS}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="join", description="Join the current Commander game")
    async def slash_join(self, interaction: discord.Interaction):
        """Join a game via slash command"""
        game = self.get_game(interaction.channel_id)

        if game.started and game.active:
            await interaction.response.send_message('The game has already started!')
            return

        if not game.players:
            await interaction.response.send_message('No game in progress. Use `/start` to start a new game.')
            return

        if game.add_player(interaction.user.id, interaction.user.display_name):
            player_list = '\n'.join([f"{i+1}. {p.username}" for i, p in enumerate(game.players.values())])

            embed = discord.Embed(
                title="Player Joined!",
                description=f"{interaction.user.display_name} joined the game.",
                color=config.COLOR_SUCCESS
            )
            embed.add_field(name="Current Players", value=player_list, inline=False)
            embed.set_footer(text=f"Players: {len(game.players)}/{config.MAX_PLAYERS}")

            await interaction.response.send_message(embed=embed)

            if len(game.players) >= config.MIN_PLAYERS and not game.started:
                embed = discord.Embed(
                    title="Ready to Begin!",
                    description="Use `/begin` to start the game, or wait for more players.",
                    color=config.COLOR_WARNING
                )
                await interaction.followup.send(embed=embed)
        else:
            if interaction.user.id in game.players:
                await interaction.response.send_message('You are already in this game!')
            else:
                await interaction.response.send_message(f'Game is full! (Max {config.MAX_PLAYERS} players)')

    @app_commands.command(name="status", description="Show the current game status")
    async def slash_status(self, interaction: discord.Interaction):
        """Show game status via slash command"""
        game = self.get_game(interaction.channel_id)

        if not game.players:
            await interaction.response.send_message('No active game. Use `/start` to begin!')
            return

        embed = discord.Embed(title="Commander Game Status", color=config.COLOR_PRIMARY)

        for player in game.players.values():
            status_lines = [f"Life: **{player.life}**"]

            if player.commander_damage:
                cmdr_dmg = [f"{game.players[pid].username}: {dmg}"
                           for pid, dmg in player.commander_damage.items()]
                status_lines.append(f"Commander Damage: {', '.join(cmdr_dmg)}")

            if player.counters:
                counter_str = ', '.join([f"{name}: {count}"
                                        for name, count in player.counters.items()])
                status_lines.append(f"Counters: {counter_str}")

            if player.is_dead():
                status_lines.append("💀 **ELIMINATED**")

            embed.add_field(name=player.username, value='\n'.join(status_lines), inline=True)

        winner = game.check_winner()
        if winner:
            embed.add_field(
                name="🏆 Winner",
                value=f"**{winner.username}** is the last player standing!",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="life", description="Modify your life total")
    @app_commands.describe(amount="Life amount (use +5 or -5 for relative changes, or 35 for absolute)")
    async def slash_life(self, interaction: discord.Interaction, amount: str):
        """Modify life via slash command"""
        game = self.get_game(interaction.channel_id)
        player = game.get_player(interaction.user.id)

        if not player:
            await interaction.response.send_message('You are not in an active game!')
            return

        try:
            if amount.startswith('+') or amount.startswith('-'):
                change = int(amount)
                player.modify_life(change)
                action = "gained" if change > 0 else "lost"
                await interaction.response.send_message(
                    f'{interaction.user.display_name} {action} {abs(change)} life. Now at **{player.life}** life.'
                )
            else:
                new_life = int(amount)
                player.set_life(new_life)
                await interaction.response.send_message(
                    f'{interaction.user.display_name} set life to **{player.life}**.'
                )

            if player.is_dead():
                await interaction.followup.send(f'💀 {interaction.user.display_name} has been eliminated!')

                winner = game.check_winner()
                if winner:
                    await interaction.followup.send(f'🏆 **{winner.username}** wins the game!')

        except ValueError:
            await interaction.response.send_message('Invalid amount. Use a number, +number, or -number.')


async def setup(bot):
    await bot.add_cog(Game(bot))
