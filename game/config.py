"""Centralized Game Configuration."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


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
            "diamond_multiplier": self.env.diamond_to_coin_multiplier,
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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameConfig":
        cfg = cls()
        if not data:
            return cfg

        # Environment
        if "grid_width" in data:
            cfg.env.grid_width = int(data["grid_width"])
        if "grid_height" in data:
            cfg.env.grid_height = int(data["grid_height"])
        if "num_coins" in data:
            cfg.env.num_coins = int(data["num_coins"])
        if "num_diamonds" in data:
            cfg.env.num_diamonds = int(data["num_diamonds"])
        if "initial_lives" in data:
            cfg.env.initial_lives = int(data["initial_lives"])
        if "max_steps" in data:
            cfg.env.max_steps_per_episode = int(data["max_steps"])
        if "diamond_multiplier" in data:
            cfg.env.diamond_to_coin_multiplier = int(data["diamond_multiplier"])

        # Rewards
        rewards = data.get("rewards", {})
        if "coin" in rewards:
            cfg.reward.collect_coin = float(rewards["coin"])
        if "convert" in rewards:
            cfg.reward.convert_diamond = float(rewards["convert"])
        if "diamond" in rewards:
            cfg.reward.collect_diamond_raw = float(rewards["diamond"])
        if "lose_life" in rewards:
            cfg.reward.lose_life = float(rewards["lose_life"])
        if "death" in rewards:
            cfg.reward.death = float(rewards["death"])
        if "exit" in rewards:
            cfg.reward.successful_exit = float(rewards["exit"])
        if "step" in rewards:
            cfg.reward.normal_step = float(rewards["step"])

        # Reinforcement Learning
        rl = data.get("rl", {})
        if "alpha" in rl:
            cfg.rl.learning_rate = float(rl["alpha"])
        if "gamma" in rl:
            cfg.rl.discount_factor = float(rl["gamma"])
        if "episodes" in rl:
            cfg.rl.training_episodes = int(rl["episodes"])

        return cfg


# Global default instance
DEFAULT_CONFIG = GameConfig()

# Dynamic active configuration
_ACTIVE_CONFIG: Optional[GameConfig] = None


def get_active_config() -> GameConfig:
    global _ACTIVE_CONFIG
    if _ACTIVE_CONFIG is None:
        try:
            from game.database.db import load_system_config, init_db
            init_db()
            saved = load_system_config("active_config")
            if saved:
                _ACTIVE_CONFIG = GameConfig.from_dict(saved)
            else:
                _ACTIVE_CONFIG = GameConfig()
        except Exception:
            _ACTIVE_CONFIG = GameConfig()
    return _ACTIVE_CONFIG


def set_active_config(cfg: GameConfig) -> GameConfig:
    global _ACTIVE_CONFIG
    _ACTIVE_CONFIG = cfg
    try:
        from game.database.db import save_system_config, init_db
        init_db()
        save_system_config(cfg.to_dict(), "active_config")
    except Exception:
        pass
    return _ACTIVE_CONFIG


def reset_active_config() -> GameConfig:
    return set_active_config(GameConfig())
