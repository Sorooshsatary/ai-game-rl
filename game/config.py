"""Centralized Game Configuration."""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class EnvironmentConfig:
    # Grid dimensions
    grid_width: int = 8
    grid_height: int = 8

    # Resource counts
    num_coins: int = 5
    num_diamonds: int = 2
    initial_lives: int = 3
    max_steps_per_episode: int = 100

    # Enemy settings
    enemy_detection_radius: int = 3  # Manhattan distance where enemy chases agent
    enemy_patrol_type: str = "bounce"  # "bounce", "clockwise", "random_safe"

    # Converter settings
    diamond_to_coin_multiplier: int = 2


@dataclass
class RewardConfig:
    # Reinforcement Learning Rewards
    collect_coin: float = 10.0
    convert_diamond: float = 20.0  # per diamond converted at Converter
    collect_diamond_raw: float = 0.5  # slight discovery reward, not main score
    lose_life: float = -15.0
    death: float = -50.0
    successful_exit: float = 5.0
    normal_step: float = -0.1
    invalid_move: float = -1.0  # hitting a wall or edge


@dataclass
class RLConfig:
    # Hyperparameters (preset, not directly tuned by child)
    learning_rate: float = 0.2
    discount_factor: float = 0.90
    initial_epsilon: float = 1.0
    final_epsilon: float = 0.05
    training_episodes: int = 30
    retrain_episodes: int = 10

    # Strategy prior strength multiplier
    prior_scale: float = 5.0


@dataclass
class GameConfig:
    env: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    reward: RewardConfig = field(default_factory=RewardConfig)
    rl: RLConfig = field(default_factory=RLConfig)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_width": self.env.grid_width,
            "grid_height": self.env.grid_height,
            "num_coins": self.env.num_coins,
            "num_diamonds": self.env.num_diamonds,
            "initial_lives": self.env.initial_lives,
            "max_steps": self.env.max_steps_per_episode,
            "rewards": {
                "coin": self.reward.collect_coin,
                "convert": self.reward.convert_diamond,
                "diamond": self.reward.collect_diamond_raw,
                "lose_life": self.reward.lose_life,
                "death": self.reward.death,
                "exit": self.reward.successful_exit,
                "step": self.reward.normal_step,
            },
            "rl": {
                "alpha": self.rl.learning_rate,
                "gamma": self.rl.discount_factor,
                "episodes": self.rl.training_episodes,
            },
        }


# Global default instance
DEFAULT_CONFIG = GameConfig()
