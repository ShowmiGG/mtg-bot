from typing import Dict, List, Optional
import config


class Player:
    """Represents a player in a Commander game"""

    def __init__(self, user_id: int, username: str):
        self.user_id = user_id
        self.username = username
        self.life = config.STARTING_LIFE
        self.commander_damage: Dict[int, int] = {}  # {opponent_user_id: damage}
        self.counters: Dict[str, int] = {}  # Custom counters (poison, energy, etc.)

    def set_life(self, amount: int):
        """Set life to a specific amount"""
        self.life = max(0, amount)

    def modify_life(self, amount: int):
        """Modify life by a relative amount (can be positive or negative)"""
        self.life = max(0, self.life + amount)

    def add_commander_damage(self, from_player_id: int, amount: int):
        """Add commander damage from another player"""
        if from_player_id not in self.commander_damage:
            self.commander_damage[from_player_id] = 0
        self.commander_damage[from_player_id] += amount

    def get_commander_damage(self, from_player_id: int) -> int:
        """Get commander damage from a specific player"""
        return self.commander_damage.get(from_player_id, 0)

    def is_dead(self) -> bool:
        """Check if player has lost the game"""
        # Life <= 0
        if self.life <= 0:
            return True

        # Commander damage >= 21
        for damage in self.commander_damage.values():
            if damage >= 21:
                return True

        # Poison counters >= 10
        if self.counters.get('poison', 0) >= 10:
            return True

        return False

    def add_counter(self, counter_name: str, amount: int = 1):
        """Add a counter (poison, energy, etc.)"""
        if counter_name not in self.counters:
            self.counters[counter_name] = 0
        self.counters[counter_name] += amount

    def get_counter(self, counter_name: str) -> int:
        """Get the count of a specific counter"""
        return self.counters.get(counter_name, 0)


class CommanderGame:
    """Represents a Commander game session"""

    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.players: Dict[int, Player] = {}  # {user_id: Player}
        self.active = False
        self.started = False

    def add_player(self, user_id: int, username: str) -> bool:
        """Add a player to the game. Returns True if successful."""
        if len(self.players) >= config.MAX_PLAYERS:
            return False

        if user_id in self.players:
            return False

        self.players[user_id] = Player(user_id, username)
        return True

    def remove_player(self, user_id: int) -> bool:
        """Remove a player from the game. Returns True if successful."""
        if user_id in self.players:
            del self.players[user_id]
            return True
        return False

    def get_player(self, user_id: int) -> Optional[Player]:
        """Get a player by user ID"""
        return self.players.get(user_id)

    def start_game(self) -> bool:
        """Start the game. Returns True if successful."""
        if len(self.players) < config.MIN_PLAYERS:
            return False

        self.active = True
        self.started = True
        return True

    def end_game(self):
        """End the current game"""
        self.active = False

    def get_alive_players(self) -> List[Player]:
        """Get list of players still alive"""
        return [p for p in self.players.values() if not p.is_dead()]

    def check_winner(self) -> Optional[Player]:
        """Check if there's a winner (only one player alive)"""
        alive = self.get_alive_players()
        if len(alive) == 1:
            return alive[0]
        return None
