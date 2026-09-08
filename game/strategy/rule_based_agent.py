"""Rule-Based Strategy Agent executing If-Then block rules."""

from typing import Tuple, List, Optional, Dict, Any
import random
from game.config import GameConfig, DEFAULT_CONFIG
from game.environment.entities import Action, Position
from game.environment.state import State
from game.strategy.rule import ChildStrategy, IfThenRule


CONDITION_NAMES_FA = {
    "enemy_near": "هیولا در نزدیکی است (فاصله ۲ خانه یا کمتر)",
    "enemy_adjacent": "هیولا در خانه مجاور است",
    "has_diamond": "الماس در کوله‌پشتی داری",
    "one_life": "فقط ۱ جان باقی مانده",
    "coins_cleared": "تمام سکه‌های نقشه جمع شده‌اند",
    "coin_exists": "سکه در نقشه وجود دارد",
    "diamond_exists": "الماس در نقشه وجود دارد",
    "always": "در هر شرایطی (همیشه)",
}

ACTION_NAMES_FA = {
    "flee_enemy": "فرار در جهت مخالف هیولا",
    "go_converter": "حرکت به سمت مبدل الماس",
    "go_exit": "حرکت به سمت درب خروج",
    "go_nearest_coin": "حرکت به سمت نزدیک‌ترین سکه",
    "go_nearest_diamond": "حرکت به سمت نزدیک‌ترین الماس",
    "random_move": "حرکت تصادفی",
}


class RuleBasedStrategyAgent:
    """Agent executing child's explicit If-Then rules sequentially.
    If no rule condition matches, it takes a random action.
    """

    def __init__(
        self,
        strategy: ChildStrategy,
        config: GameConfig = DEFAULT_CONFIG,
        agent_id: str = "strategy_player",
        seed: Optional[int] = None,
    ):
        self.strategy = strategy
        self.config = config
        self.agent_id = agent_id
        self.total_steps = 0
        self.rng = random.Random(seed)

    def get_legal_actions(self, state: State) -> List[Action]:
        return state.get_legal_actions()

    def _best_step_towards(self, current: Position, target: Position, legal_actions: List[Action]) -> Action:
        best_act = legal_actions[0]
        min_dist = 9999
        for act in legal_actions:
            np = current.move(act)
            dist = np.manhattan_distance(target)
            if dist < min_dist:
                min_dist = dist
                best_act = act
        return best_act

    def _best_step_away_from(self, current: Position, threat: Position, legal_actions: List[Action]) -> Action:
        best_act = legal_actions[0]
        max_dist = -1
        for act in legal_actions:
            np = current.move(act)
            dist = np.manhattan_distance(threat)
            if dist > max_dist:
                max_dist = dist
                best_act = act
        return best_act

    def _check_condition(self, condition: str, state: State) -> bool:
        if condition == "enemy_near":
            return state.enemy_dist <= 2
        elif condition == "enemy_adjacent":
            return state.enemy_dist <= 1
        elif condition == "has_diamond":
            return state.diamonds_held > 0
        elif condition == "one_life":
            return state.lives <= 1
        elif condition == "coins_cleared":
            return state.total_coins_remaining == 0
        elif condition == "coin_exists":
            return state.nearest_coin_pos is not None
        elif condition == "diamond_exists":
            return state.nearest_diamond_pos is not None
        elif condition == "always":
            return True
        return False

    def _execute_action_rule(self, action_name: str, state: State, legal_actions: List[Action]) -> Optional[Action]:
        if action_name == "flee_enemy":
            return self._best_step_away_from(state.agent_pos, state.enemy_pos, legal_actions)
        elif action_name == "go_converter":
            return self._best_step_towards(state.agent_pos, state.converter_pos, legal_actions)
        elif action_name == "go_exit":
            return self._best_step_towards(state.agent_pos, state.exit_pos, legal_actions)
        elif action_name == "go_nearest_coin":
            if state.nearest_coin_pos is not None:
                return self._best_step_towards(state.agent_pos, state.nearest_coin_pos, legal_actions)
            return None
        elif action_name == "go_nearest_diamond":
            if state.nearest_diamond_pos is not None:
                return self._best_step_towards(state.agent_pos, state.nearest_diamond_pos, legal_actions)
            return None
        elif action_name == "random_move":
            return self.rng.choice(legal_actions)
        return None

    def select_action(self, state: State) -> Tuple[Action, str]:
        legal_actions = self.get_legal_actions(state)
        self.total_steps += 1

        # Check child's If-Then rules in order of priority
        for idx, rule in enumerate(self.strategy.if_then_rules, 1):
            if self._check_condition(rule.condition, state):
                action = self._execute_action_rule(rule.action, state, legal_actions)
                if action is not None:
                    cond_fa = CONDITION_NAMES_FA.get(rule.condition, rule.condition)
                    act_fa = ACTION_NAMES_FA.get(rule.action, rule.action)
                    reason = f"شرط {idx} برقرار شد: اگر {cond_fa} ➔ {act_fa}"
                    return action, reason

        # Fallback: No rule matched! Perform random move
        fallback_action = self.rng.choice(legal_actions)
        reason = "هیچ شرطی برای این وضعیت پیدا نشد؛ ربات گیج شد و حرکت تصادفی کرد!"
        return fallback_action, reason
