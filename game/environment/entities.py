"""Entities and data structures for the game environment."""

from dataclasses import dataclass
from enum import IntEnum
from typing import Tuple, List, Optional, Dict, Any


class Action(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    @classmethod
    def from_string(cls, name: str) -> "Action":
        name = name.strip().upper()
        mapping = {
            "UP": cls.UP,
            "DOWN": cls.DOWN,
            "LEFT": cls.LEFT,
            "RIGHT": cls.RIGHT,
        }
        if name in mapping:
            return mapping[name]
        raise ValueError(f"Unknown action: {name}")

    def to_offset(self) -> Tuple[int, int]:
        """Returns (dx, dy) where dx is col change and dy is row change.
        UP: dy = -1, DOWN: dy = +1, LEFT: dx = -1, RIGHT: dx = +1.
        """
        if self == Action.UP:
            return (0, -1)
        elif self == Action.DOWN:
            return (0, 1)
        elif self == Action.LEFT:
            return (-1, 0)
        elif self == Action.RIGHT:
            return (1, 0)
        return (0, 0)

    def fa_name(self) -> str:
        names = {
            Action.UP: "بالا",
            Action.DOWN: "پایین",
            Action.LEFT: "چپ",
            Action.RIGHT: "راست",
        }
        return names.get(self, self.name)


@dataclass(frozen=True)
class Position:
    x: int  # col
    y: int  # row

    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def manhattan_distance(self, other: "Position") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def move(self, action: Action) -> "Position":
        dx, dy = action.to_offset()
        return Position(self.x + dx, self.y + dy)

    def relative_direction(self, target: "Position") -> Optional[Action]:
        """Returns the primary cardinal Action to get closer to target."""
        dx = target.x - self.x
        dy = target.y - self.y
        if dx == 0 and dy == 0:
            return None

        # Prioritize whichever axis has greater displacement, or pick one
        if abs(dx) >= abs(dy):
            return Action.RIGHT if dx > 0 else Action.LEFT
        else:
            return Action.DOWN if dy > 0 else Action.UP


@dataclass
class AgentStatus:
    agent_id: str
    position: Position
    lives: int = 3
    coins: int = 0
    diamonds: int = 0
    is_alive: bool = True
    has_exited: bool = False
    total_reward: float = 0.0
    steps_taken: int = 0

    def copy(self) -> "AgentStatus":
        return AgentStatus(
            agent_id=self.agent_id,
            position=self.position,
            lives=self.lives,
            coins=self.coins,
            diamonds=self.diamonds,
            is_alive=self.is_alive,
            has_exited=self.has_exited,
            total_reward=self.total_reward,
            steps_taken=self.steps_taken,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "x": self.position.x,
            "y": self.position.y,
            "lives": self.lives,
            "coins": self.coins,
            "diamonds": self.diamonds,
            "is_alive": self.is_alive,
            "has_exited": self.has_exited,
            "total_reward": round(self.total_reward, 2),
            "steps_taken": self.steps_taken,
        }
