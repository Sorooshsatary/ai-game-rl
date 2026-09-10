"""Converts Child Strategy into initial Q-values (Priors)."""

from typing import Dict, Tuple, List, Optional
from game.config import GameConfig, DEFAULT_CONFIG
from game.environment.entities import Action, Position
from game.environment.state import State
from game.strategy.rule import ChildStrategy


class StrategyPriorEngine:
    """Evaluates state-action pairs using child strategy rules to generate Q_initial(s, a)."""

    def __init__(self, strategy: ChildStrategy, config: Optional[GameConfig] = None):
        self.strategy = strategy
        self.config = config or DEFAULT_CONFIG

    def compute_action_prior(self, state: State, action: Action) -> Tuple[float, List[str]]:
        """Computes Q_initial for a specific action in a given state, plus explanation tags."""
        reasons: List[str] = []
        q_value = 0.0

        # Hypothetical new position
        new_pos = state.agent_pos.move(action)

        # 1. Bounds check
        if not (0 <= new_pos.x < state.grid_width and 0 <= new_pos.y < state.grid_height):
            return -5.0, ["دیوار یا خارج از نقشه"]

        # Manhattan delta calculations (positive = got closer, negative = moved farther)
        def delta_dist(target: Optional[Position]) -> int:
            if target is None:
                return 0
            curr_d = state.agent_pos.manhattan_distance(target)
            new_d = new_pos.manhattan_distance(target)
            return curr_d - new_d  # +1 if closer, -1 if farther, 0 if perpendicular/same

        delta_coin = delta_dist(state.nearest_coin_pos)
        delta_diamond = delta_dist(state.nearest_diamond_pos)
        delta_converter = delta_dist(state.converter_pos)
        delta_exit = delta_dist(state.exit_pos)
        delta_enemy = delta_dist(state.enemy_pos)  # +1 means stepping closer to danger!

        # Dynamic reward scaling factors relative to default baseline
        rew = self.config.reward
        exit_rew = getattr(rew, "successful_exit", 25.0)
        coin_rew = getattr(rew, "collect_coin", 10.0)
        convert_rew = getattr(rew, "convert_diamond", 20.0)
        police_penalty = abs(getattr(rew, "lose_life", 10.0))

        exit_scale = max(0.2, exit_rew / 25.0)
        coin_scale = max(0.05, coin_rew / 10.0)
        convert_scale = max(0.1, convert_rew / 20.0)
        enemy_scale = max(0.2, police_penalty / 10.0)

        # Detect rush exit scenario (either rules or reward shaping dominant exit)
        should_rush_exit = False
        if self.strategy.rules.get("exit_if_coins_cleared", False) and state.total_coins_remaining == 0:
            should_rush_exit = True
            reasons.append("تمام شدن سکه‌ها - رفتن به سمت مسیر فرار و خروج")

        if self.strategy.rules.get("exit_if_one_life", False) and state.lives <= 1 and state.coins_held > 0:
            should_rush_exit = True
            reasons.append("جان اندک - اولویت فرار و حفظ غنایم")

        # Step count condition from If-Then rules
        for r in getattr(self.strategy, "if_then_rules", []):
            if getattr(r, "action", "") in ("go_exit", "flee_towards_exit"):
                for c in getattr(r, "conditions", []):
                    if getattr(c, "type", "") == "steps_gt" and state.step_count > getattr(c, "value", 20):
                        should_rush_exit = True
                        reasons.append(f"سپری شدن بیش از {c.value} گام - اولویت فرار و خروج")

        # Reward-driven rush exit: when exit reward vastly exceeds coin reward (e.g. rush_exit preset)
        is_reward_rush_exit = (coin_rew <= 3.0) or (exit_rew / max(0.1, coin_rew) >= 4.0)
        if is_reward_rush_exit:
            should_rush_exit = True

        # 2. Coin Evaluation
        if state.nearest_coin_pos is not None:
            coin_weight = self.strategy.coin_priority * 0.6 * coin_scale
            if is_reward_rush_exit:
                coin_weight *= 0.1  # Strongly suppress detours for low-value coins
            if delta_coin > 0:
                q_value += coin_weight
                reasons.append(f"نزدیک شدن به سکه (+{coin_weight:.1f})")
            elif delta_coin < 0:
                q_value -= coin_weight * 0.3

        # 3. Diamond Evaluation
        if state.nearest_diamond_pos is not None:
            diamond_weight = self.strategy.diamond_priority * 0.5 * convert_scale
            if is_reward_rush_exit:
                diamond_weight *= 0.1
            # Rule: diamond_only_if_safe
            if self.strategy.rules.get("diamond_only_if_safe", False) and state.enemy_dist <= 2:
                diamond_weight *= 0.2  # De-prioritize diamond when enemy lurks near!

            if delta_diamond > 0:
                q_value += diamond_weight
                reasons.append(f"نزدیک شدن به کلید گنج (+{diamond_weight:.1f})")
            elif delta_diamond < 0:
                q_value -= diamond_weight * 0.2

        # 4. Converter Evaluation (when holding diamonds)
        if state.diamonds_held > 0:
            converter_weight = self.strategy.converter_urgency * 0.8 * convert_scale
            if self.strategy.rules.get("deposit_before_coins", False):
                converter_weight *= 1.5  # Extra urgency

            if delta_converter > 0:
                q_value += converter_weight
                reasons.append(f"حمل کلید و باز کردن صندوق گنج (+{converter_weight:.1f})")
            elif delta_converter < 0:
                q_value -= converter_weight * 0.4

        # 5. Enemy Danger & Survival
        enemy_weight = self.strategy.enemy_fear * 1.0 * enemy_scale
        if state.enemy_dist <= 3:
            # Danger zone
            if new_pos == state.enemy_pos:
                # Stepping directly into enemy!
                penalty = enemy_weight * 3.0
                q_value -= penalty
                reasons.append(f"خطر دستگیری توسط پلیس (-{penalty:.1f})")
            elif delta_enemy > 0:
                # Moving closer to enemy
                penalty = enemy_weight * 1.5
                q_value -= penalty
                reasons.append(f"نزدیک شدن خطرناک به پلیس (-{penalty:.1f})")
            elif delta_enemy < 0:
                # Moving away from enemy
                bonus = enemy_weight * 1.0
                q_value += bonus
                reasons.append(f"فرار و دور شدن از پلیس (+{bonus:.1f})")

            # Check intercept with enemy's heading trajectory
            if not state.enemy_stunned:
                enemy_next_step = state.enemy_pos.move(state.enemy_heading)
                if new_pos == enemy_next_step:
                    traj_penalty = enemy_weight * 2.0
                    q_value -= traj_penalty
                    reasons.append(f"مسیر در جهت حرکت گشت پلیس است (-{traj_penalty:.1f})")

            # Rule: flee_adjacent_enemy
            if self.strategy.rules.get("flee_adjacent_enemy", False) and state.enemy_dist <= 1:
                if delta_enemy <= 0:
                    q_value += 3.0
                    reasons.append("قانون فرار اضطراری از پلیس مجاور")

        # 6. Exit Evaluation
        exit_weight = self.strategy.exit_eagerness * 0.6 * exit_scale

        if should_rush_exit:
            exit_weight *= 3.0

        if delta_exit > 0:
            q_value += exit_weight
            if should_rush_exit:
                if is_reward_rush_exit:
                    reasons.append(f"شتاب فرار مستقیم به سوی خروج (+{exit_weight:.1f})")
                else:
                    reasons.append(f"حرکت به سوی در خروج (+{exit_weight:.1f})")
        elif delta_exit < 0 and should_rush_exit:
            q_value -= exit_weight * 0.8

        # 7. Direction Continuity (heading momentum)
        if action == state.agent_heading:
            q_value += 0.15

        return round(q_value, 2), reasons

    def compute_all_priors(self, state: State) -> Dict[Action, Tuple[float, List[str]]]:
        """Computes Q_initial for all 4 cardinal actions."""
        return {
            act: self.compute_action_prior(state, act)
            for act in [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
        }
