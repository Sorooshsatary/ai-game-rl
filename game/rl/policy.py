"""Policies for action selection in Q-learning."""

import random
from typing import Dict, List, Tuple
from game.environment.entities import Action


class Policy:
    @staticmethod
    def select_action(
        q_values: Dict[Action, float],
        epsilon: float = 0.0,
        rng: random.Random = random,
    ) -> Tuple[Action, bool]:
        """Selects action using epsilon-greedy strategy.
        Returns (selected_action, was_exploratory).
        """
        all_actions = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]

        # 1. Explore
        if epsilon > 0 and rng.random() < epsilon:
            return rng.choice(all_actions), True

        # 2. Exploit: Find best action(s)
        max_q = max(q_values.values())
        best_actions = [act for act, q in q_values.items() if abs(q - max_q) < 1e-6]

        # Break ties randomly among best
        chosen = rng.choice(best_actions)
        return chosen, False
