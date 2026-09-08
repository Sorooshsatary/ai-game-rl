"""Trainer managing multi-episode training, progression, and replay history."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from game.config import GameConfig, DEFAULT_CONFIG
from game.environment.rules import GameEnvironment
from game.rl.exploration import EpsilonDecay
from game.rl.q_learning import QLearningAgent
from game.strategy.rule import ChildStrategy
from game.replay.replay import EpisodeReplay
from game.training.episode import run_episode


@dataclass
class TrainingMetrics:
    episode_id: int
    epsilon: float
    total_reward: float
    coins_exited: int
    coins_collected: int
    diamonds_converted: int
    lives_remaining: int
    steps_taken: int
    success: bool
    termination_reason: str


@dataclass
class TrainingResult:
    total_episodes: int
    metrics: List[TrainingMetrics]
    replays: Dict[int, EpisodeReplay]  # keyed by episode_id
    final_success_rate: float
    avg_reward_last_5: float
    strategy_divergence_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_episodes": self.total_episodes,
            "metrics": [
                {
                    "episode": m.episode_id,
                    "epsilon": round(m.epsilon, 3),
                    "total_reward": round(m.total_reward, 1),
                    "coins_exited": m.coins_exited,
                    "coins_collected": m.coins_collected,
                    "diamonds_converted": m.diamonds_converted,
                    "lives": m.lives_remaining,
                    "steps": m.steps_taken,
                    "success": m.success,
                    "termination": m.termination_reason,
                }
                for m in self.metrics
            ],
            "available_replay_episodes": list(self.replays.keys()),
            "final_success_rate": round(self.final_success_rate, 2),
            "avg_reward_last_5": round(self.avg_reward_last_5, 1),
            "strategy_divergence_count": self.strategy_divergence_count,
        }


class Trainer:
    def __init__(
        self,
        strategy: ChildStrategy,
        config: GameConfig = DEFAULT_CONFIG,
        agent: Optional[QLearningAgent] = None,
        mode: str = "pure",
    ):
        self.config = config
        self.strategy = strategy
        self.mode = mode
        self.agent = agent or QLearningAgent(strategy=strategy, config=config, mode=mode)
        self.env = GameEnvironment(config=config)
        self.history_replays: Dict[int, EpisodeReplay] = {}
        self.all_metrics: List[TrainingMetrics] = []
        self.total_episodes_completed: int = 0

    def reset(self):
        """Completely resets agent knowledge, Q-table, and metrics."""
        self.agent = QLearningAgent(strategy=self.strategy, config=self.config, mode=self.mode)
        self.history_replays.clear()
        self.all_metrics.clear()
        self.total_episodes_completed = 0

    def train(
        self,
        num_episodes: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int, TrainingMetrics], None]] = None,
    ) -> TrainingResult:
        """Trains the agent across randomized maps, continuing from previous learning."""
        episodes_to_run = num_episodes or self.config.rl.training_episodes
        self.agent.unlock_for_training()

        decay_rate = 0.96

        # Run episodes continuing from total_episodes_completed
        for i in range(1, episodes_to_run + 1):
            self.total_episodes_completed += 1
            ep_num = self.total_episodes_completed

            # Epsilon decays progressively across cumulative episodes
            epsilon = max(
                self.config.rl.final_epsilon,
                self.config.rl.initial_epsilon * (decay_rate ** (ep_num - 1)),
            )

            replay = run_episode(
                env=self.env,
                agent=self.agent,
                epsilon=epsilon,
                episode_id=ep_num,
            )

            metric = TrainingMetrics(
                episode_id=ep_num,
                epsilon=epsilon,
                total_reward=replay.total_reward,
                coins_exited=replay.coins_exited,
                coins_collected=replay.coins_collected,
                diamonds_converted=replay.diamonds_converted,
                lives_remaining=replay.lives_remaining,
                steps_taken=replay.steps_taken,
                success=replay.success,
                termination_reason=replay.termination_reason,
            )
            self.all_metrics.append(metric)

            # Store replay (store every episode if <= 50, otherwise milestones)
            if self.total_episodes_completed <= 50 or ep_num in [1, 5, 10, 20, 30, 50, 75, 100] or replay.success:
                self.history_replays[ep_num] = replay

            if progress_callback:
                progress_callback(i, episodes_to_run, metric)

        # Calculate summary metrics over recent episodes
        last_5 = self.all_metrics[-5:] if len(self.all_metrics) >= 5 else self.all_metrics
        success_rate = sum(1 for m in last_5 if m.success) / len(last_5) if last_5 else 0.0
        avg_reward = sum(m.total_reward for m in last_5) / len(last_5) if last_5 else 0.0

        # Measure divergence from prior
        divergence_count = 0
        for state_key, q_dict in self.agent.q_table.items():
            if state_key in self.agent.prior_table:
                prior_best = max(self.agent.prior_table[state_key], key=self.agent.prior_table[state_key].get)
                learned_best = max(q_dict, key=q_dict.get)
                if prior_best != learned_best:
                    divergence_count += 1

        return TrainingResult(
            total_episodes=self.total_episodes_completed,
            metrics=list(self.all_metrics),
            replays=self.history_replays,
            final_success_rate=success_rate,
            avg_reward_last_5=avg_reward,
            strategy_divergence_count=divergence_count,
        )

    def retrain_with_new_strategy(
        self,
        new_strategy: ChildStrategy,
        from_scratch: bool = True,
        num_episodes: Optional[int] = None,
    ) -> TrainingResult:
        """Called when the child revises strategy after seeing replays."""
        self.strategy = new_strategy
        if from_scratch:
            self.reset()
        else:
            self.agent.update_strategy(new_strategy, retrain_from_scratch=False)

        episodes = num_episodes or (
            self.config.rl.training_episodes if from_scratch else self.config.rl.retrain_episodes
        )
        return self.train(num_episodes=episodes)
