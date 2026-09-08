"""Multi-Agent Arena where multiple trained agents compete simultaneously for shared resources."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import random
from game.config import GameConfig, DEFAULT_CONFIG
from game.environment.entities import Position, Action, AgentStatus
from game.environment.enemy import Enemy
from game.environment.grid import GridMap
from game.environment.state import State
from game.rl.q_learning import QLearningAgent
from game.competition.leaderboard import Leaderboard, LeaderboardEntry


@dataclass
class ArenaAgentWrapper:
    agent_id: str
    name: str
    color: str
    agent: QLearningAgent
    status: AgentStatus


@dataclass
class ArenaStepFrame:
    step_index: int
    agents: List[Dict[str, Any]]
    enemy: Dict[str, Any]
    coins_left: List[List[int]]
    diamonds_left: List[List[int]]
    events: List[str]


@dataclass
class ArenaMatchResult:
    map_config: Dict[str, Any]
    leaderboard: List[LeaderboardEntry]
    frames: List[ArenaStepFrame]
    total_steps: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "map_config": self.map_config,
            "leaderboard": [e.to_dict() for e in self.leaderboard],
            "total_steps": self.total_steps,
            "frames": [
                {
                    "step": f.step_index,
                    "agents": f.agents,
                    "enemy": f.enemy,
                    "coins": f.coins_left,
                    "diamonds": f.diamonds_left,
                    "events": f.events,
                }
                for f in self.frames
            ],
        }


class MultiAgentArena:
    def __init__(
        self,
        config: GameConfig = DEFAULT_CONFIG,
        grid_width: int = 10,  # Slightly larger grid for multi-agent competition
        grid_height: int = 10,
        num_coins: int = 8,
        num_diamonds: int = 3,
        seed: Optional[int] = None,
    ):
        self.config = config
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.num_coins = num_coins
        self.num_diamonds = num_diamonds
        self.seed = seed
        self.rng = random.Random(seed)

    def _create_unseen_map(self, num_agents: int) -> Tuple[GridMap, List[Position], Position]:
        """Generates a completely unseen map ensuring distinct spawn points for all competitors."""
        all_coords = [(x, y) for x in range(self.grid_width) for y in range(self.grid_height)]
        self.rng.shuffle(all_coords)

        idx = 0
        agent_spawns = []
        for _ in range(num_agents):
            agent_spawns.append(Position(*all_coords[idx]))
            idx += 1

        exit_pos = Position(*all_coords[idx])
        idx += 1

        converter_pos = Position(*all_coords[idx])
        idx += 1

        enemy_spawn = Position(*all_coords[idx])
        idx += 1

        coins = set()
        for _ in range(self.num_coins):
            if idx < len(all_coords):
                coins.add(Position(*all_coords[idx]))
                idx += 1

        diamonds = set()
        for _ in range(self.num_diamonds):
            if idx < len(all_coords):
                diamonds.add(Position(*all_coords[idx]))
                idx += 1

        grid_map = GridMap(
            width=self.grid_width,
            height=self.grid_height,
            converter_pos=converter_pos,
            exit_pos=exit_pos,
            coins=coins,
            diamonds=diamonds,
        )
        return grid_map, agent_spawns, enemy_spawn

    def run_match(
        self,
        competitors: List[Tuple[str, str, str, QLearningAgent]],  # (agent_id, name, color, agent)
        max_steps: int = 120,
    ) -> ArenaMatchResult:
        """Runs simultaneous simulation with all competitors locked into greedy policy."""
        grid_map, spawns, enemy_spawn = self._create_unseen_map(len(competitors))

        wrappers: List[ArenaAgentWrapper] = []
        for idx, (aid, name, color, agent) in enumerate(competitors):
            agent.lock_for_competition()  # Lock learning and exploration
            status = AgentStatus(
                agent_id=aid,
                position=spawns[idx],
                lives=self.config.env.initial_lives,
            )
            wrappers.append(ArenaAgentWrapper(aid, name, color, agent, status))

        enemy = Enemy(
            position=enemy_spawn,
            detection_radius=self.config.env.enemy_detection_radius,
        )

        frames: List[ArenaStepFrame] = []
        step_idx = 0

        # Save initial frame 0
        frames.append(
            ArenaStepFrame(
                step_index=0,
                agents=[
                    {**w.status.to_dict(), "name": w.name, "color": w.color}
                    for w in wrappers
                ],
                enemy=enemy.to_dict(),
                coins_left=[[p.x, p.y] for p in grid_map.coins],
                diamonds_left=[[p.x, p.y] for p in grid_map.diamonds],
                events=["آغاز مسابقه در میدان رقابت"],
            )
        )

        while step_idx < max_steps:
            step_idx += 1
            step_events: List[str] = []

            # Check if all agents finished
            active_wrappers = [w for w in wrappers if w.status.is_alive and not w.status.has_exited]
            if not active_wrappers:
                step_events.append("تمامی شرکت‌کنندگان به کار خود پایان دادند.")
                break

            # 1. Agents select and execute actions
            for w in active_wrappers:
                # Build agent-specific egocentric State
                nearest_coin = min(
                    grid_map.coins,
                    key=lambda p: w.status.position.manhattan_distance(p),
                    default=None,
                )
                nearest_diamond = min(
                    grid_map.diamonds,
                    key=lambda p: w.status.position.manhattan_distance(p),
                    default=None,
                )

                agent_state = State(
                    agent_pos=w.status.position,
                    enemy_pos=enemy.position,
                    nearest_coin_pos=nearest_coin,
                    nearest_diamond_pos=nearest_diamond,
                    converter_pos=grid_map.converter_pos,
                    exit_pos=grid_map.exit_pos,
                    lives=w.status.lives,
                    coins_held=w.status.coins,
                    diamonds_held=w.status.diamonds,
                    total_coins_remaining=len(grid_map.coins),
                    grid_width=grid_map.width,
                    grid_height=grid_map.height,
                    walls=set(grid_map.walls),
                )

                # Select action (locked greedy)
                action, _, _, _ = w.agent.select_action(agent_state, epsilon=0.0)

                # Move
                new_pos = w.status.position.move(action)
                if grid_map.is_valid_position(new_pos):
                    w.status.position = new_pos
                w.status.steps_taken += 1

                # Cell triggers
                # Coin (Shared resource! First to step gets it)
                if w.status.position in grid_map.coins:
                    grid_map.coins.remove(w.status.position)
                    w.status.coins += 1
                    step_events.append(f"{w.name} یک سکه برداشت! 🪙")

                # Diamond (Shared resource!)
                if w.status.position in grid_map.diamonds:
                    grid_map.diamonds.remove(w.status.position)
                    w.status.diamonds += 1
                    step_events.append(f"{w.name} یک الماس پیدا کرد! 💎")

                # Converter
                if w.status.position == grid_map.converter_pos and w.status.diamonds > 0:
                    converted = w.status.diamonds * self.config.env.diamond_to_coin_multiplier
                    w.status.coins += converted
                    step_events.append(f"{w.name} {w.status.diamonds} الماس را به {converted} سکه تبدیل کرد! 🏪")
                    w.status.diamonds = 0

                # Exit
                if w.status.position == grid_map.exit_pos:
                    w.status.has_exited = True
                    step_events.append(f"{w.name} با موفقیت از خروج خارج شد! 🚪 ({w.status.coins} سکه)")

            # 2. Enemy Move
            live_agents_pos = [
                w.status.position for w in wrappers if w.status.is_alive and not w.status.has_exited
            ]
            if live_agents_pos:
                enemy.position = enemy.choose_move(
                    agent_positions=live_agents_pos,
                    grid_width=grid_map.width,
                    grid_height=grid_map.height,
                    forbidden_positions=[grid_map.exit_pos] + list(grid_map.walls),
                )

                # Check collisions
                for w in wrappers:
                    if w.status.is_alive and not w.status.has_exited:
                        if w.status.position == enemy.position:
                            w.status.lives -= 1
                            step_events.append(f"هیولا به {w.name} ضربه زد! (-۱ جان) ❤️")
                            if w.status.lives <= 0:
                                w.status.is_alive = False
                                step_events.append(f"{w.name} توسط هیولا حذف شد! 💀")

            # Record frame
            frames.append(
                ArenaStepFrame(
                    step_index=step_idx,
                    agents=[
                        {**w.status.to_dict(), "name": w.name, "color": w.color}
                        for w in wrappers
                    ],
                    enemy=enemy.to_dict(),
                    coins_left=[[p.x, p.y] for p in grid_map.coins],
                    diamonds_left=[[p.x, p.y] for p in grid_map.diamonds],
                    events=step_events,
                )
            )

        # 3. Calculate Final Leaderboard
        competitor_summaries = []
        for w in wrappers:
            coins_exited = w.status.coins if w.status.has_exited else 0
            competitor_summaries.append(
                {
                    "agent_id": w.agent_id,
                    "agent_name": w.name,
                    "strategy_name": w.agent.strategy.name,
                    "coins_exited": coins_exited,
                    "lives": w.status.lives,
                    "steps": w.status.steps_taken,
                    "is_alive": w.status.is_alive,
                    "has_exited": w.status.has_exited,
                }
            )

        leaderboard = Leaderboard.rank_competitors(competitor_summaries)

        return ArenaMatchResult(
            map_config=grid_map.to_dict(),
            leaderboard=leaderboard,
            frames=frames,
            total_steps=step_idx,
        )
