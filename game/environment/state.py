"""State Representation and Relative Feature Extraction for Generalization."""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any, Set
from game.environment.entities import Position, Action


def get_relative_direction(agent: Position, target: Optional[Position]) -> str:
    """Returns UP, DOWN, LEFT, RIGHT, or NONE based on relative position."""
    if target is None:
        return "NONE"
    dx = target.x - agent.x
    dy = target.y - agent.y
    if dx == 0 and dy == 0:
        return "HERE"

    # Determine primary direction
    if abs(dx) > abs(dy):
        return "RIGHT" if dx > 0 else "LEFT"
    elif abs(dy) > abs(dx):
        return "DOWN" if dy > 0 else "UP"
    else:
        # Diagonal tie-breaker
        return "RIGHT" if dx > 0 else "LEFT"


def get_quadrant_direction(agent: Position, target: Optional[Position]) -> Tuple[int, int]:
    """Returns sign tuple (sign(dx), sign(dy)) for relative direction."""
    if target is None:
        return (0, 0)
    dx = target.x - agent.x
    dy = target.y - agent.y
    sx = 1 if dx > 0 else (-1 if dx < 0 else 0)
    sy = 1 if dy > 0 else (-1 if dy < 0 else 0)
    return (sx, sy)


@dataclass
class State:
    agent_pos: Position
    enemy_pos: Position
    nearest_coin_pos: Optional[Position]
    nearest_diamond_pos: Optional[Position]
    converter_pos: Position
    exit_pos: Position
    lives: int
    coins_held: int
    diamonds_held: int
    total_coins_remaining: int
    grid_width: int
    grid_height: int
    walls: Set[Position] = field(default_factory=set)
    coins: List[Position] = field(default_factory=list)
    diamonds: List[Position] = field(default_factory=list)

    def get_legal_actions(self) -> List[Action]:
        """Returns list of actions that stay within grid bounds and avoid walls."""
        legal = []
        for act in Action:
            np = self.agent_pos.move(act)
            if (
                0 <= np.x < self.grid_width
                and 0 <= np.y < self.grid_height
                and np not in self.walls
            ):
                legal.append(act)
        return legal if legal else [Action.UP]

    @property
    def enemy_dist(self) -> int:
        return self.agent_pos.manhattan_distance(self.enemy_pos)

    @property
    def nearest_coin_dist(self) -> int:
        if self.nearest_coin_pos is None:
            return 999
        return self.agent_pos.manhattan_distance(self.nearest_coin_pos)

    @property
    def nearest_diamond_dist(self) -> int:
        if self.nearest_diamond_pos is None:
            return 999
        return self.agent_pos.manhattan_distance(self.nearest_diamond_pos)

    @property
    def converter_dist(self) -> int:
        return self.agent_pos.manhattan_distance(self.converter_pos)

    @property
    def exit_dist(self) -> int:
        return self.agent_pos.manhattan_distance(self.exit_pos)

    def is_enemy_in_line_of_sight(self) -> bool:
        """Returns True if agent and enemy share the same row or col with no walls between."""
        if self.agent_pos.x == self.enemy_pos.x:
            min_y = min(self.agent_pos.y, self.enemy_pos.y)
            max_y = max(self.agent_pos.y, self.enemy_pos.y)
            for y in range(min_y + 1, max_y):
                if Position(self.agent_pos.x, y) in self.walls:
                    return False
            return True
        elif self.agent_pos.y == self.enemy_pos.y:
            min_x = min(self.agent_pos.x, self.enemy_pos.x)
            max_x = max(self.agent_pos.x, self.enemy_pos.x)
            for x in range(min_x + 1, max_x):
                if Position(x, self.agent_pos.y) in self.walls:
                    return False
            return True
        return False

    def is_enemy_blocked_by_wall(self) -> bool:
        """Returns True if a wall directly separates the agent and enemy within radius 3."""
        if self.enemy_dist > 3:
            return False
        min_x = min(self.agent_pos.x, self.enemy_pos.x)
        max_x = max(self.agent_pos.x, self.enemy_pos.x)
        min_y = min(self.agent_pos.y, self.enemy_pos.y)
        max_y = max(self.agent_pos.y, self.enemy_pos.y)
        for w in self.walls:
            if min_x <= w.x <= max_x and min_y <= w.y <= max_y:
                return True
        return False

    def to_discrete(self) -> Tuple:
        """Returns a hashable compact discrete representation that generalizes across maps.
        
        Features:
        1. coin_dir: Direction to nearest coin (UP, DOWN, LEFT, RIGHT, NONE)
        2. diamond_dir: Direction to nearest diamond
        3. converter_dir: Direction to converter (only active if carrying diamond)
        4. exit_dir: Direction to exit
        5. enemy_threat:
           - 'SAFE' if dist > 2
           - 'DANGER_UP', 'DANGER_DOWN', 'DANGER_LEFT', 'DANGER_RIGHT' if dist <= 2
           - 'ADJACENT_UP', etc. if dist == 1
        6. has_diamond: bool (carrying diamond)
        7. coins_status: 'NONE_LEFT' if total_coins_remaining == 0 else 'HAS_MAP_COINS'
        8. low_lives: bool (lives <= 1)
        """
        # 1. Coin direction
        coin_dir = get_relative_direction(self.agent_pos, self.nearest_coin_pos)

        # 2. Diamond direction
        diamond_dir = get_relative_direction(self.agent_pos, self.nearest_diamond_pos)

        # 3. Converter direction (only relevant if holding diamond)
        has_diamond = self.diamonds_held > 0
        converter_dir = get_relative_direction(self.agent_pos, self.converter_pos) if has_diamond else "NONE"

        # 4. Exit direction
        exit_dir = get_relative_direction(self.agent_pos, self.exit_pos)

        # 5. Enemy threat
        dist = self.enemy_dist
        if dist > 3:
            enemy_threat = "SAFE"
        elif dist <= 1:
            enemy_threat = f"ADJ_{get_relative_direction(self.agent_pos, self.enemy_pos)}"
        elif dist == 2:
            enemy_threat = f"DANGER_{get_relative_direction(self.agent_pos, self.enemy_pos)}"
        else:  # dist == 3
            enemy_threat = f"WARN_{get_relative_direction(self.agent_pos, self.enemy_pos)}"

        # 6. Map coins
        coins_status = "ZERO_LEFT" if self.total_coins_remaining == 0 else "AVAILABLE"

        # 7. Low lives
        low_lives = self.lives <= 1

        return (
            coin_dir,
            diamond_dir,
            converter_dir,
            exit_dir,
            enemy_threat,
            has_diamond,
            coins_status,
            low_lives,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Human-readable dictionary for logging and UI inspection."""
        return {
            "agent_pos": [self.agent_pos.x, self.agent_pos.y],
            "enemy_pos": [self.enemy_pos.x, self.enemy_pos.y],
            "nearest_coin_pos": [self.nearest_coin_pos.x, self.nearest_coin_pos.y] if self.nearest_coin_pos else None,
            "nearest_diamond_pos": [self.nearest_diamond_pos.x, self.nearest_diamond_pos.y] if self.nearest_diamond_pos else None,
            "converter_pos": [self.converter_pos.x, self.converter_pos.y],
            "exit_pos": [self.exit_pos.x, self.exit_pos.y],
            "distances": {
                "coin": self.nearest_coin_dist,
                "diamond": self.nearest_diamond_dist,
                "converter": self.converter_dist,
                "exit": self.exit_dist,
                "enemy": self.enemy_dist,
            },
            "lives": self.lives,
            "coins_held": self.coins_held,
            "diamonds_held": self.diamonds_held,
            "total_coins_remaining": self.total_coins_remaining,
            "coins": [[p.x, p.y] for p in self.coins],
            "diamonds": [[p.x, p.y] for p in self.diamonds],
            "discrete_state": list(self.to_discrete()),
        }
