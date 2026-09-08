"""Training Package."""

from game.training.episode import run_episode
from game.training.trainer import Trainer, TrainingResult, TrainingMetrics
from game.training.comparison import AgentComparisonEngine, DualComparisonResult, AgentRunSummary

__all__ = [
    "run_episode",
    "Trainer",
    "TrainingResult",
    "TrainingMetrics",
    "AgentComparisonEngine",
    "DualComparisonResult",
    "AgentRunSummary",
]

