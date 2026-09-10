"""Q-Learning agent with Prior Seeding from Child Strategy and Competition Lock."""

from typing import Dict, Tuple, Optional, Any, List
import random
from game.config import GameConfig, DEFAULT_CONFIG
from game.environment.entities import Action
from game.environment.state import State
from game.rl.policy import Policy
from game.strategy.rule import ChildStrategy
from game.strategy.strategy_to_prior import StrategyPriorEngine


class QLearningAgent:
    def __init__(
        self,
        strategy: Optional[ChildStrategy] = None,
        config: GameConfig = DEFAULT_CONFIG,
        agent_id: str = "player",
        seed: Optional[int] = None,
        mode: str = "pure",  # "pure" (starts Q=0) or "hybrid" (seeds Q from strategy prior)
    ):
        from game.strategy.strategy_builder import StrategyBuilder
        self.strategy = strategy or StrategyBuilder.get_presets()["balanced"]
        self.config = config
        self.agent_id = agent_id
        self.mode = mode
        self.prior_engine = StrategyPriorEngine(self.strategy, config=self.config)
        self.rng = random.Random(seed)

        # Q-table: discrete_state -> {Action: float}
        self.q_table: Dict[Tuple, Dict[Action, float]] = {}

        # Cache of prior values for reference and UI comparison
        self.prior_table: Dict[Tuple, Dict[Action, float]] = {}

        # Competition lock: when True, epsilon=0 and no updates are made
        self.locked: bool = False

        # Learning stats
        self.total_updates = 0

    def get_initial_prior(self, state: State) -> Dict[Action, float]:
        """Calculates child strategy prior for all actions in this state."""
        discrete = state.to_discrete()
        priors = self.prior_engine.compute_all_priors(state)
        curr_priors = {act: round(val, 2) for act, (val, _) in priors.items()}
        self.prior_table[discrete] = curr_priors
        return curr_priors

    def get_q_values(self, state: State) -> Dict[Action, float]:
        """Returns Q-values for all actions.
        In 'pure' mode, unseen states start with Q(s, a) = 0.0.
        In 'hybrid' mode, unseen states are seeded with child strategy prior.
        """
        discrete = state.to_discrete()
        if discrete not in self.q_table:
            if self.mode == "hybrid":
                priors = self.get_initial_prior(state)
                self.q_table[discrete] = dict(priors)
            else:
                self.q_table[discrete] = {act: 0.0 for act in Action}
        return self.q_table[discrete]

    def select_action(
        self,
        state: State,
        epsilon: float = 0.0,
        legal_actions: Optional[List[Action]] = None,
    ) -> Tuple[Action, bool, Dict[Action, float], Dict[Action, float]]:
        """Selects action using epsilon-greedy (or greedy if locked) among legal actions.
        Returns (action, was_exploratory, current_q_values, prior_q_values).
        """
        curr_q = self.get_q_values(state)
        prior_q = self.get_initial_prior(state)

        if legal_actions is None:
            legal_actions = state.get_legal_actions()

        effective_epsilon = 0.0 if self.locked else epsilon
        chosen_action, was_exploratory = Policy.select_action(
            q_values=curr_q,
            epsilon=effective_epsilon,
            rng=self.rng,
            legal_actions=legal_actions,
        )
        return chosen_action, was_exploratory, dict(curr_q), dict(prior_q)

    def update(
        self,
        state: State,
        action: Action,
        reward: float,
        next_state: State,
        done: bool,
    ) -> float:
        """Executes Bellman equation update.
        Returns td_error.
        """
        if self.locked:
            return 0.0

        discrete_s = state.to_discrete()
        current_q = self.get_q_values(state)[action]

        alpha = self.config.rl.learning_rate
        gamma = self.config.rl.discount_factor

        if done:
            target = reward
        else:
            next_q_values = self.get_q_values(next_state)
            next_legal = next_state.get_legal_actions()
            max_next_q = max(next_q_values[a] for a in next_legal) if next_legal else max(next_q_values.values())
            target = reward + gamma * max_next_q

        td_error = target - current_q
        new_q = current_q + alpha * td_error
        self.q_table[discrete_s][action] = round(new_q, 4)
        self.total_updates += 1

        return td_error

    def lock_for_competition(self):
        """Locks policy: learning=off, epsilon=0."""
        self.locked = True

    def unlock_for_training(self):
        self.locked = False

    def update_strategy(self, new_strategy: ChildStrategy, retrain_from_scratch: bool = True):
        """Allows child to modify strategy and optionally reset Q-table."""
        self.strategy = new_strategy
        self.prior_engine = StrategyPriorEngine(new_strategy, config=self.config)
        self.prior_table.clear()
        if retrain_from_scratch:
            self.q_table.clear()
            self.total_updates = 0

    def update_config(self, new_config: GameConfig, reset_q: bool = False):
        """Updates active game/reward config and syncs prior engine."""
        self.config = new_config
        self.prior_engine = StrategyPriorEngine(self.strategy, config=new_config)
        self.prior_table.clear()
        if reset_q:
            self.q_table.clear()
            self.total_updates = 0

    def get_stats(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "num_states_learned": len(self.q_table),
            "total_updates": self.total_updates,
            "locked": self.locked,
            "strategy": self.strategy.to_dict(),
        }
