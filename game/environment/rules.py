"""Environment execution engine, transitions, rewards, and rules."""

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional, List
from game.config import GameConfig, DEFAULT_CONFIG
from game.environment.entities import Position, Action, AgentStatus
from game.environment.enemy import Enemy
from game.environment.grid import GridMap
from game.environment.state import State


@dataclass
class StepResult:
    next_state: State
    reward: float
    done: bool
    events: List[str]
    info: Dict[str, Any]


class GameEnvironment:
    def __init__(
        self,
        config: GameConfig = DEFAULT_CONFIG,
        grid_map: Optional[GridMap] = None,
        agent_start: Optional[Position] = None,
        enemy_start: Optional[Position] = None,
        seed: Optional[int] = None,
    ):
        self.config = config
        self.seed = seed

        if grid_map is None:
            self.grid_map, self.agent_start, self.enemy_start = GridMap.generate_random(
                width=config.env.grid_width,
                height=config.env.grid_height,
                num_coins=config.env.num_coins,
                num_diamonds=config.env.num_diamonds,
                agent_start_pos=agent_start,
                enemy_start_pos=enemy_start,
                seed=seed,
            )
        else:
            self.grid_map = grid_map.copy()
            self.agent_start = agent_start or Position(0, 0)
            self.enemy_start = enemy_start or Position(config.env.grid_width - 1, config.env.grid_height - 1)

        self.agent = AgentStatus(
            agent_id="player",
            position=self.agent_start,
            lives=config.env.initial_lives,
        )
        self.enemy = self._create_enemy(self.enemy_start)
        self.current_step = 0
        self.done = False

    def _create_enemy(self, pos: Position) -> Enemy:
        strictness = getattr(self.config.env, "enemy_strictness", "normal")
        det_radius = self.config.env.enemy_detection_radius
        if strictness == "lenient":
            det_radius = min(det_radius, 2)
        elif strictness == "strict":
            det_radius = max(det_radius, 5)
        elif strictness == "nightmare":
            det_radius = max(det_radius, 16)

        return Enemy(
            position=pos,
            detection_radius=det_radius,
            strictness=strictness,
        )

    def reset(self, new_map: bool = True, seed: Optional[int] = None) -> State:
        """Resets the environment for a new episode."""
        if seed is not None:
            self.seed = seed

        if new_map:
            self.grid_map, self.agent_start, self.enemy_start = GridMap.generate_random(
                width=self.config.env.grid_width,
                height=self.config.env.grid_height,
                num_coins=self.config.env.num_coins,
                num_diamonds=self.config.env.num_diamonds,
                seed=self.seed,
            )
        else:
            # Re-seed coins and diamonds from original positions if saved, or regenerate
            pass

        self.agent = AgentStatus(
            agent_id="player",
            position=self.agent_start,
            lives=self.config.env.initial_lives,
        )
        self.enemy = self._create_enemy(self.enemy_start)
        self.current_step = 0
        self.done = False
        return self.get_state()

    def get_nearest_item(self, items: set) -> Optional[Position]:
        if not items:
            return None
        return min(items, key=lambda p: self.agent.position.manhattan_distance(p))

    def get_state(self) -> State:
        nearest_coin = self.get_nearest_item(self.grid_map.coins)
        nearest_diamond = self.get_nearest_item(self.grid_map.diamonds)

        return State(
            agent_pos=self.agent.position,
            enemy_pos=self.enemy.position,
            nearest_coin_pos=nearest_coin,
            nearest_diamond_pos=nearest_diamond,
            converter_pos=self.grid_map.converter_pos,
            exit_pos=self.grid_map.exit_pos,
            lives=self.agent.lives,
            coins_held=self.agent.coins,
            diamonds_held=self.agent.diamonds,
            total_coins_remaining=len(self.grid_map.coins),
            grid_width=self.grid_map.width,
            grid_height=self.grid_map.height,
            walls=set(self.grid_map.walls),
            coins=list(self.grid_map.coins),
            diamonds=list(self.grid_map.diamonds),
            enemy_stunned=self.enemy.stun_timer > 0,
            stun_timer=self.enemy.stun_timer,
            agent_heading=self.agent.heading,
            enemy_heading=self.enemy.patrol_direction,
            step_count=self.current_step,
        )

    def step(self, action: Action) -> StepResult:
        if self.done:
            return StepResult(self.get_state(), 0.0, True, ["ALREADY_DONE"], {})

        self.current_step += 1
        self.agent.steps_taken += 1
        self.agent.heading = action
        reward = 0.0
        events: List[str] = []

        prev_agent_pos = self.agent.position
        prev_enemy_pos = self.enemy.position

        # 1. Agent Move
        new_pos = self.agent.position.move(action)
        if not self.grid_map.is_valid_position(new_pos):
            # Invalid move (hit wall or out of bounds)
            reward += self.config.reward.invalid_move
            events.append("INVALID_MOVE")
        else:
            self.agent.position = new_pos
            reward += self.config.reward.normal_step
            events.append(f"MOVE_{action.name}")

        # Check immediate collision with enemy upon stepping (if enemy is active)
        hit_by_enemy = False
        if self.agent.position == self.enemy.position and self.enemy.stun_timer <= 0:
            hit_by_enemy = True

        # 2. Cell interactions (Coin, Diamond, Converter, Exit)
        # Coin
        if self.agent.position in self.grid_map.coins:
            self.grid_map.coins.remove(self.agent.position)
            self.agent.coins += 1
            reward += self.config.reward.collect_coin
            events.append("COLLECT_COIN")

        # Diamond
        if self.agent.position in self.grid_map.diamonds:
            self.grid_map.diamonds.remove(self.agent.position)
            self.agent.diamonds += 1
            reward += self.config.reward.collect_diamond_raw
            events.append("COLLECT_DIAMOND")

        # Converter
        if self.agent.position == self.grid_map.converter_pos:
            if self.agent.diamonds > 0:
                num_converted = self.agent.diamonds
                added_coins = num_converted * self.config.env.diamond_to_coin_multiplier
                self.agent.coins += added_coins
                reward += self.config.reward.convert_diamond * num_converted
                self.agent.diamonds = 0
                events.append(f"CONVERT_DIAMOND_{num_converted}_TO_{added_coins}_COINS")

        # Exit
        if self.agent.position == self.grid_map.exit_pos:
            self.agent.has_exited = True
            coin_bonus = self.agent.coins * getattr(self.config.reward, "exit_coin_bonus", 5.0)
            reward += self.config.reward.successful_exit + coin_bonus
            events.append("EXIT_SUCCESS")
            self.done = True

        # 3. Enemy Turn (if not exited)
        if not self.done:
            forbidden = [self.grid_map.exit_pos] + list(self.grid_map.walls)  # Enemy cannot block exit or pass through walls
            # If agent didn't already step directly into enemy, enemy takes its turn
            if not hit_by_enemy:
                self.enemy.position = self.enemy.choose_move(
                    agent_positions=[self.agent.position],
                    grid_width=self.grid_map.width,
                    grid_height=self.grid_map.height,
                    forbidden_positions=forbidden,
                )

                # Check collision after enemy move
                if self.enemy.position == self.agent.position and self.enemy.stun_timer <= 0:
                    hit_by_enemy = True

        # 4. Handle Enemy Damage
        if hit_by_enemy:
            self.agent.lives -= 1
            reward += self.config.reward.lose_life
            events.append("ENEMY_HIT")

            if self.agent.lives <= 0:
                self.agent.is_alive = False
                reward += self.config.reward.death
                events.append("DEATH")
                self.done = True
            else:
                # Stun enemy based on strictness: lenient (3), normal (2), strict/nightmare (1)
                strictness = getattr(self.config.env, "enemy_strictness", "normal")
                stun_duration = 3 if strictness == "lenient" else (1 if strictness in ("strict", "nightmare") else 2)
                self.enemy.stun_timer = stun_duration
                events.append("ENEMY_STUNNED")

                # If overlapping, separate them by 1 tile so they remain clearly visible
                if self.enemy.position == self.agent.position:
                    if prev_enemy_pos != self.agent.position and self.grid_map.is_valid_position(prev_enemy_pos):
                        self.enemy.position = prev_enemy_pos
                    elif prev_agent_pos != self.enemy.position and self.grid_map.is_valid_position(prev_agent_pos):
                        self.agent.position = prev_agent_pos
                    else:
                        for act in [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]:
                            cand = self.enemy.position.move(act)
                            if (
                                self.grid_map.is_valid_position(cand)
                                and cand != self.agent.position
                                and cand != self.grid_map.exit_pos
                            ):
                                self.enemy.position = cand
                                break

        # 5. Check Step Limit
        if not self.done and self.current_step >= self.config.env.max_steps_per_episode:
            self.done = True
            reward += getattr(self.config.reward, "timeout", -10.0)
            events.append("TIMEOUT")

        self.agent.total_reward += reward
        next_state = self.get_state()

        return StepResult(
            next_state=next_state,
            reward=reward,
            done=self.done,
            events=events,
            info={
                "step": self.current_step,
                "agent": self.agent.to_dict(),
                "enemy": self.enemy.to_dict(),
                "coins_left": len(self.grid_map.coins),
                "diamonds_left": len(self.grid_map.diamonds),
            },
        )
