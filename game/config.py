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
    lose_life: float = -10.0
    death: float = -25.0
    successful_exit: float = 25.0
    exit_coin_bonus: float = 5.0  # Bonus per coin brought home through exit
    normal_step: float = -0.05
    invalid_move: float = -1.0  # hitting a wall or edge


import os
import json

@dataclass
class RLConfig:
    # Hyperparameters (configurable via Admin Panel and config.json)
    learning_rate: float = 0.2
    discount_factor: float = 0.90
    initial_epsilon: float = 1.0
    final_epsilon: float = 0.05
    epsilon_decay: float = 0.96
    training_episodes: int = 10
    retrain_episodes: int = 10

    # Strategy prior strength multiplier
    prior_scale: float = 5.0


@dataclass
class GameConfig:
    env: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    reward: RewardConfig = field(default_factory=RewardConfig)
    rl: RLConfig = field(default_factory=RLConfig)
    show_presets: bool = False  # Admin flag: display ready-made strategy presets for normal users
    show_reward_tuning: bool = False  # Admin flag: display reward tuning lab in RL section for normal users
    show_part2: bool = False  # Admin flag: lock/unlock Part 2 (AI & Dual Comparison) for normal users
    show_extra_strategies: bool = False  # Admin flag: unlock extra advanced strategy presets
    unlock_advanced_rules: bool = False  # Admin flag: unlock 2 advanced conditions and 2 advanced actions
    anti_loop_enabled: bool = False  # Admin flag: break periodic oscillation between thief and enemy with random moves
    difficulty: str = "normal"  # "easy" (interactive questionnaire) vs "normal" (If-Then rule blocks)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_width": self.env.grid_width,
            "grid_height": self.env.grid_height,
            "num_coins": self.env.num_coins,
            "num_diamonds": self.env.num_diamonds,
            "initial_lives": self.env.initial_lives,
            "max_steps": self.env.max_steps_per_episode,
            "diamond_multiplier": self.env.diamond_to_coin_multiplier,
            "show_presets": self.show_presets,
            "show_reward_tuning": self.show_reward_tuning,
            "show_part2": self.show_part2,
            "show_extra_strategies": self.show_extra_strategies,
            "unlock_advanced_rules": self.unlock_advanced_rules,
            "anti_loop_enabled": self.anti_loop_enabled,
            "difficulty": self.difficulty,
            "rewards": {
                "coin": self.reward.collect_coin,
                "convert": self.reward.convert_diamond,
                "diamond": self.reward.collect_diamond_raw,
                "lose_life": self.reward.lose_life,
                "death": self.reward.death,
                "exit": self.reward.successful_exit,
                "exit_coin_bonus": self.reward.exit_coin_bonus,
                "step": self.reward.normal_step,
            },
            "rl": {
                "alpha": self.rl.learning_rate,
                "gamma": self.rl.discount_factor,
                "initial_epsilon": self.rl.initial_epsilon,
                "final_epsilon": self.rl.final_epsilon,
                "epsilon_decay": self.rl.epsilon_decay,
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
        if "show_presets" in data:
            cfg.show_presets = bool(data["show_presets"])
        if "show_reward_tuning" in data:
            cfg.show_reward_tuning = bool(data["show_reward_tuning"])
        if "show_part2" in data:
            cfg.show_part2 = bool(data["show_part2"])
        if "show_extra_strategies" in data:
            cfg.show_extra_strategies = bool(data["show_extra_strategies"])
        if "unlock_advanced_rules" in data:
            cfg.unlock_advanced_rules = bool(data["unlock_advanced_rules"])
        if "anti_loop_enabled" in data:
            cfg.anti_loop_enabled = bool(data["anti_loop_enabled"])
        if "difficulty" in data:
            cfg.difficulty = str(data["difficulty"])

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
        if "exit_coin_bonus" in rewards:
            cfg.reward.exit_coin_bonus = float(rewards["exit_coin_bonus"])
        if "step" in rewards:
            cfg.reward.normal_step = float(rewards["step"])

        # Reinforcement Learning
        rl = data.get("rl", {})
        if "alpha" in rl or "learning_rate" in rl:
            cfg.rl.learning_rate = float(rl.get("alpha", rl.get("learning_rate")))
        if "gamma" in rl or "discount_factor" in rl:
            cfg.rl.discount_factor = float(rl.get("gamma", rl.get("discount_factor")))
        if "initial_epsilon" in rl or "epsilon_init" in rl:
            cfg.rl.initial_epsilon = float(rl.get("initial_epsilon", rl.get("epsilon_init")))
        if "final_epsilon" in rl or "epsilon_min" in rl:
            cfg.rl.final_epsilon = float(rl.get("final_epsilon", rl.get("epsilon_min")))
        if "epsilon_decay" in rl or "decay_rate" in rl:
            cfg.rl.epsilon_decay = float(rl.get("epsilon_decay", rl.get("decay_rate")))
        if "episodes" in rl or "training_episodes" in rl:
            cfg.rl.training_episodes = int(rl.get("episodes", rl.get("training_episodes")))

        return cfg


# Global default instance
DEFAULT_CONFIG = GameConfig()

# Dynamic active configuration
_ACTIVE_CONFIG: Optional[GameConfig] = None

CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")


def _save_to_file(cfg: GameConfig):
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg.to_dict(), f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _load_from_file() -> Optional[GameConfig]:
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return GameConfig.from_dict(data)
        except Exception:
            pass
    return None


def get_active_config() -> GameConfig:
    global _ACTIVE_CONFIG
    if _ACTIVE_CONFIG is None:
        # 1. Try to load from config.json
        file_cfg = _load_from_file()
        if file_cfg:
            _ACTIVE_CONFIG = file_cfg
        else:
            # 2. Try to load from DB
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
            # Write config.json for disk persistence
            _save_to_file(_ACTIVE_CONFIG)
    return _ACTIVE_CONFIG


def set_active_config(cfg: GameConfig) -> GameConfig:
    global _ACTIVE_CONFIG
    _ACTIVE_CONFIG = cfg
    # Save to database
    try:
        from game.database.db import save_system_config, init_db
        init_db()
        save_system_config(cfg.to_dict(), "active_config")
    except Exception:
        pass
    # Save to config.json file
    _save_to_file(cfg)
    return _ACTIVE_CONFIG


def reset_active_config() -> GameConfig:
    return set_active_config(GameConfig())

