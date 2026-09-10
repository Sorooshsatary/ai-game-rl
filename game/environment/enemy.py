"""Dynamic Enemy with predictable chase and patrol behavior."""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import random
from game.environment.entities import Position, Action


@dataclass
class Enemy:
    position: Position
    detection_radius: int = 3
    patrol_direction: Action = Action.RIGHT
    patrol_axis: str = "horizontal"  # "horizontal" or "vertical"
    stun_timer: int = 0
    strictness: str = "normal"  # "lenient", "normal", "strict", "nightmare"

    def copy(self) -> "Enemy":
        return Enemy(
            position=self.position,
            detection_radius=self.detection_radius,
            patrol_direction=self.patrol_direction,
            patrol_axis=self.patrol_axis,
            stun_timer=self.stun_timer,
            strictness=self.strictness,
        )

    def _patrol_step(
        self,
        grid_width: int,
        grid_height: int,
        forbidden_positions: List[Position],
    ) -> Position:
        """Standard back-and-forth bounce patrol behavior."""
        next_pos = self.position.move(self.patrol_direction)
        in_bounds = (
            0 <= next_pos.x < grid_width
            and 0 <= next_pos.y < grid_height
            and next_pos not in forbidden_positions
        )
        if in_bounds:
            return next_pos
        else:
            reverse_map = {
                Action.UP: Action.DOWN,
                Action.DOWN: Action.UP,
                Action.LEFT: Action.RIGHT,
                Action.RIGHT: Action.LEFT,
            }
            self.patrol_direction = reverse_map[self.patrol_direction]
            bounce_pos = self.position.move(self.patrol_direction)
            if (
                0 <= bounce_pos.x < grid_width
                and 0 <= bounce_pos.y < grid_height
                and bounce_pos not in forbidden_positions
            ):
                return bounce_pos
            return self.position

    def choose_move(
        self,
        agent_positions: List[Position],
        grid_width: int,
        grid_height: int,
        forbidden_positions: Optional[List[Position]] = None,
    ) -> Position:
        """Choose next position based on nearest agent within detection radius, or patrol."""
        if self.stun_timer > 0:
            self.stun_timer -= 1
            return self.position

        if forbidden_positions is None:
            forbidden_positions = []

        # Find nearest agent
        nearest_agent: Optional[Position] = None
        min_dist = float("inf")

        for ap in agent_positions:
            dist = self.position.manhattan_distance(ap)
            if dist < min_dist:
                min_dist = dist
                nearest_agent = ap

        # Case 1: Agent within detection radius -> chase nearest agent
        if nearest_agent is not None and min_dist <= self.detection_radius:
            # Lenient police: 25% chance of sleepy distraction (keeps routine patrol instead of instant chase)
            if self.strictness == "lenient" and random.random() < 0.25:
                return self._patrol_step(grid_width, grid_height, forbidden_positions)

            best_pos = self.position
            best_dist = min_dist

            candidate_actions = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
            if self.strictness in ("strict", "nightmare"):
                # Strict / Nightmare: prioritize direct intercept without random shuffling
                candidate_actions.sort(key=lambda a: self.position.move(a).manhattan_distance(nearest_agent))
            else:
                random.shuffle(candidate_actions)

            for act in candidate_actions:
                new_pos = self.position.move(act)
                if 0 <= new_pos.x < grid_width and 0 <= new_pos.y < grid_height:
                    if new_pos not in forbidden_positions:
                        d = new_pos.manhattan_distance(nearest_agent)
                        if d < best_dist:
                            best_dist = d
                            best_pos = new_pos

            return best_pos

        # Case 2: Outside detection radius -> Patrol predictably
        return self._patrol_step(grid_width, grid_height, forbidden_positions)

    def to_dict(self) -> dict:
        return {
            "x": self.position.x,
            "y": self.position.y,
            "detection_radius": self.detection_radius,
            "patrol_direction": self.patrol_direction.name,
            "stun_timer": self.stun_timer,
            "is_stunned": self.stun_timer > 0,
            "strictness": self.strictness,
        }
