"""Policies for action selection in Q-learning."""

import random
from typing import Dict, List, Tuple, Optional
from game.environment.entities import Action


class Policy:
    @staticmethod
    def select_action(
        q_values: Dict[Action, float],
        epsilon: float = 0.0,
        rng: random.Random = random,
        legal_actions: Optional[List[Action]] = None,
    ) -> Tuple[Action, bool]:
        """Selects action using epsilon-greedy strategy among legal actions.
        Returns (selected_action, was_exploratory).
        """
        available_actions = (
            [a for a in legal_actions if a in q_values]
            if legal_actions is not None and len(legal_actions) > 0
            else list(q_values.keys())
        )
        if not available_actions:
            available_actions = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]

        # 1. Explore among legal actions
        if epsilon > 0 and rng.random() < epsilon:
            return rng.choice(available_actions), True

        # 2. Exploit: Find best action(s) strictly among legal actions
        max_q = max(q_values[act] for act in available_actions)
        best_actions = [act for act in available_actions if abs(q_values[act] - max_q) < 1e-6]

        # Break ties randomly among best legal actions
        chosen = rng.choice(best_actions)
        return chosen, False
