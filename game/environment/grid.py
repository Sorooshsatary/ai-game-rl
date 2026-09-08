"""Grid map representation and procedural generation."""

from dataclasses import dataclass, field
from typing import Set, List, Optional, Dict, Any, Tuple
import random
from game.environment.entities import Position, Action


@dataclass
class GridMap:
    width: int
    height: int
    converter_pos: Position
    exit_pos: Position
    coins: Set[Position] = field(default_factory=set)
    diamonds: Set[Position] = field(default_factory=set)
    walls: Set[Position] = field(default_factory=set)

    def is_valid_position(self, pos: Position) -> bool:
        """Check if position is inside bounds and not a wall."""
        return (
            0 <= pos.x < self.width
            and 0 <= pos.y < self.height
            and pos not in self.walls
        )

    def copy(self) -> "GridMap":
        return GridMap(
            width=self.width,
            height=self.height,
            converter_pos=self.converter_pos,
            exit_pos=self.exit_pos,
            coins=set(self.coins),
            diamonds=set(self.diamonds),
            walls=set(self.walls),
        )

    @classmethod
    def generate_random(
        cls,
        width: int = 8,
        height: int = 8,
        num_coins: int = 5,
        num_diamonds: int = 2,
        agent_start_pos: Optional[Position] = None,
        enemy_start_pos: Optional[Position] = None,
        seed: Optional[int] = None,
    ) -> Tuple["GridMap", Position, Position]:
        """Procedurally generates a randomized map with all entities placed distinctly.
        Returns (grid_map, agent_start, enemy_start).
        """
        rng = random.Random(seed)

        all_coords = [(x, y) for x in range(width) for y in range(height)]
        rng.shuffle(all_coords)

        idx = 0

        # 1. Agent start
        if agent_start_pos is None:
            agent_start_pos = Position(*all_coords[idx])
            idx += 1

        # 2. Exit (place at a reasonable distance from agent)
        exit_pos = None
        for i in range(idx, len(all_coords)):
            candidate = Position(*all_coords[i])
            if candidate.manhattan_distance(agent_start_pos) >= max(3, (width + height) // 3):
                exit_pos = candidate
                all_coords.pop(i)
                break
        if exit_pos is None:
            exit_pos = Position(*all_coords[idx])
            idx += 1

        # 3. Converter
        converter_pos = Position(*all_coords[idx])
        idx += 1

        # 4. Enemy start (ensure fair initial distance >= 3 from agent)
        enemy_start_pos_final = None
        if enemy_start_pos is not None:
            enemy_start_pos_final = enemy_start_pos
        else:
            for i in range(idx, len(all_coords)):
                candidate = Position(*all_coords[i])
                if candidate.manhattan_distance(agent_start_pos) >= 3:
                    enemy_start_pos_final = candidate
                    all_coords.pop(i)
                    break
            if enemy_start_pos_final is None:
                enemy_start_pos_final = Position(*all_coords[idx])
                idx += 1

        # 5. Coins
        coins = set()
        for _ in range(num_coins):
            if idx < len(all_coords):
                coins.add(Position(*all_coords[idx]))
                idx += 1

        # 6. Diamonds
        diamonds = set()
        for _ in range(num_diamonds):
            if idx < len(all_coords):
                diamonds.add(Position(*all_coords[idx]))
                idx += 1

        grid_map = cls(
            width=width,
            height=height,
            converter_pos=converter_pos,
            exit_pos=exit_pos,
            coins=coins,
            diamonds=diamonds,
        )
        return grid_map, agent_start_pos, enemy_start_pos_final

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "converter": [self.converter_pos.x, self.converter_pos.y],
            "exit": [self.exit_pos.x, self.exit_pos.y],
            "coins": [[p.x, p.y] for p in self.coins],
            "diamonds": [[p.x, p.y] for p in self.diamonds],
            "walls": [[p.x, p.y] for p in self.walls],
        }
