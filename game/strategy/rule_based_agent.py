"""Rule-Based Strategy Agent executing If-Then block rules."""

from typing import Tuple, List, Optional, Dict, Any, Set
import random
from game.config import GameConfig, DEFAULT_CONFIG
from game.environment.entities import Action, Position
from game.environment.state import State
from game.strategy.rule import ChildStrategy, IfThenRule, ConditionItem


def format_condition_fa(cond: ConditionItem) -> str:
    t = cond.type
    v = cond.value
    if t == "enemy_dist_le":
        return f"فاصله تا هیولا ≤ {v}"
    elif t == "enemy_dist_gt":
        return f"فاصله تا هیولا > {v} (محیط امن)"
    elif t == "enemy_adjacent" or (t == "enemy_dist_le" and v == 1):
        return "هیولا در خانه مجاور"
    elif t == "enemy_near":
        return "هیولا در نزدیکی (فاصله ≤ ۲)"
    elif t == "coin_dist_le":
        return f"فاصله تا نزدیک‌ترین سکه ≤ {v}"
    elif t == "diamond_dist_le":
        return f"فاصله تا نزدیک‌ترین الماس ≤ {v}"
    elif t == "converter_dist_le":
        return f"فاصله تا مبدل الماس ≤ {v}"
    elif t == "exit_dist_le":
        return f"فاصله تا در خروج ≤ {v}"
    elif t == "steps_gt":
        return f"تعداد گام‌ها > {v}"
    elif t == "steps_le":
        return f"تعداد گام‌ها ≤ {v}"
    elif t == "has_diamond":
        return "الماس در کوله‌پشتی داری"
    elif t == "one_life":
        return "فقط ۱ جان باقی مانده"
    elif t == "coins_cleared":
        return "تمام سکه‌ها جمع شده‌اند"
    elif t == "coin_exists":
        return "سکه در نقشه وجود دارد"
    elif t == "diamond_exists":
        return "الماس در نقشه وجود دارد"
    elif t == "always":
        return "همیشه"
    return t


CONDITION_NAMES_FA = {
    "enemy_dist_le": "فاصله تا پلیس (هیولا) کمتر یا مساوی مقدار",
    "enemy_dist_gt": "فاصله تا پلیس (هیولا) بیشتر از مقدار (محیط امن)",
    "enemy_near": "پلیس (هیولا) در نزدیکی (فاصله ۲ یا کمتر)",
    "enemy_adjacent": "پلیس (هیولا) در خانه مجاور",
    "steps_gt": "تعداد گام‌های طی شده بیشتر از مقدار",
    "steps_le": "تعداد گام‌های طی شده کمتر یا مساوی مقدار",
    "coin_dist_le": "فاصله تا نزدیک‌ترین سکه کمتر یا مساوی مقدار",
    "diamond_dist_le": "فاصله تا نزدیک‌ترین کلید گنج (الماس) کمتر یا مساوی مقدار",
    "converter_dist_le": "فاصله تا صندوق گنج (مبدل) کمتر یا مساوی مقدار",
    "exit_dist_le": "فاصله تا مسیر فرار و در خروج کمتر یا مساوی مقدار",
    "has_diamond": "کلید گنج (الماس در کوله‌پشتی داری)",
    "one_life": "فقط ۱ جان باقی مانده",
    "coins_cleared": "تمام سکه‌های نقشه جمع شده‌اند",
    "coin_exists": "سکه در نقشه وجود دارد",
    "diamond_exists": "کلید گنج (الماس) در نقشه وجود دارد",
    "always": "در هر شرایطی (همیشه)",
}

ACTION_NAMES_FA = {
    "flee_enemy": "فرار هوشمند شاه‌دزد از پلیس (هیولا)",
    "flee_dodge": "جاخالی دادن و چرخش تاکتیکی شاه‌دزد از پلیس",
    "flee_collect": "فرار فرصت‌طلبانه (سرقت سکه در مسیر فرار از پلیس)",
    "flee_towards_exit": "فرار هوشمند شاه‌دزد از پلیس با گرایش به در خروج",
    "flee_towards_converter": "فرار هوشمند شاه‌دزد از پلیس با گرایش به صندوق گنج (مبدل)",
    "patrol_safe": "گشت‌زنی امن شاه‌دزد دور از پلیس (هیولا)",
    "go_converter": "حرکت شاه‌دزد به سمت صندوق گنج (مبدل) جهت باز کردن با کلید",
    "go_exit": "حرکت شاه‌دزد به سمت درب خروج و مسیر فرار",
    "go_nearest_coin": "حرکت شاه‌دزد به سمت نزدیک‌ترین سکه",
    "go_nearest_diamond": "حرکت شاه‌دزد به سمت نزدیک‌ترین کلید گنج (الماس)",
    "random_move": "حرکت تصادفی",
}


def check_line_of_sight(p1: Position, p2: Position, walls: Set[Position]) -> bool:
    """Checks if p1 and p2 have direct unobstructed line of sight without walls in between."""
    if p1.x == p2.x:
        min_y = min(p1.y, p2.y)
        max_y = max(p1.y, p2.y)
        for y in range(min_y + 1, max_y):
            if Position(p1.x, y) in walls:
                return False
        return True
    elif p1.y == p2.y:
        min_x = min(p1.x, p2.x)
        max_x = max(p1.x, p2.x)
        for x in range(min_x + 1, max_x):
            if Position(x, p1.y) in walls:
                return False
        return True
    return False


class RuleBasedStrategyAgent:
    """Agent executing child's explicit If-Then rules sequentially.
    Supports logical AND across multiple conditions and distance thresholds.
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


    def _smart_flee(
        self,
        current: Position,
        threat: Position,
        legal_actions: List[Action],
        state: State,
        bias_target: Optional[Position] = None,
        style: str = "balanced",
    ) -> Tuple[Action, int, int]:
        """Smart flee maximizing distance from threat, avoiding dead ends and cul-de-sacs,
        predicting enemy pursuit, and executing tactical dodging maneuvers.
        Returns: (chosen_action, curr_dist, new_dist)
        """
        curr_dist = current.manhattan_distance(threat)
        curr_los = check_line_of_sight(current, threat, state.walls)
        best_act = legal_actions[0]
        best_score = -999999.0

        # Predict enemy's direct charge / next patrol step if not stunned
        enemy_next_step = None
        if not state.enemy_stunned:
            enemy_next_step = threat.move(state.enemy_heading)

        # Opposite of previous heading (to avoid rapid 2-step oscillation)
        reverse_act = None
        if state.agent_heading is not None:
            rev_map = {
                Action.UP: Action.DOWN,
                Action.DOWN: Action.UP,
                Action.LEFT: Action.RIGHT,
                Action.RIGHT: Action.LEFT,
            }
            reverse_act = rev_map.get(state.agent_heading)

        for act in legal_actions:
            next_pos = current.move(act)
            new_dist = next_pos.manhattan_distance(threat)

            # Degree of freedom: count safe non-wall exits from next_pos
            open_exits = 0.0
            for cand in Action:
                p = next_pos.move(cand)
                if (
                    0 <= p.x < state.grid_width
                    and 0 <= p.y < state.grid_height
                    and p not in state.walls
                    and p != threat
                ):
                    # Exit is substantially safer if not adjacent to active threat
                    if state.enemy_stunned or p.manhattan_distance(threat) > 1:
                        open_exits += 1.0
                    else:
                        open_exits += 0.3

            # Base distance and escape mobility scoring
            score = (new_dist * 60.0) + (open_exits * 20.0)

            # Dead-end avoidance: heavily penalize alcoves, corners, and cul-de-sacs
            if open_exits == 0:
                score -= 1500.0
            elif open_exits <= 1.0:
                score -= 500.0

            # Immediate danger penalties
            if next_pos == threat:
                score -= 3000.0  # Stepping directly into enemy
            elif not state.enemy_stunned and new_dist <= 1:
                # Adjacent to active enemy: enemy will step into agent on its turn!
                score -= 800.0
            elif new_dist < curr_dist:
                score -= 400.0  # Moving closer to threat

            # Intercept prevention: avoid enemy's predicted next step
            if enemy_next_step is not None and next_pos == enemy_next_step:
                score -= 700.0

            # Tactical style adjustments
            if style == "dodge":
                next_los = check_line_of_sight(next_pos, threat, state.walls)
                # 1. Break Line of Sight (slip behind cover or out of charge corridor)
                if curr_los and not next_los:
                    score += 35.0
                elif not curr_los and next_los:
                    score -= 25.0

                # 2. Tactical lateral sidestep when in direct line with threat
                if current.x == threat.x and next_pos.x != current.x:
                    score += 20.0
                elif current.y == threat.y and next_pos.y != current.y:
                    score += 20.0

                # 3. Prevent rapid oscillation back into previous tile if multiple open exits exist
                if act == reverse_act and open_exits >= 2.0:
                    score -= 20.0

            elif style == "collect":
                # Opportunistic flee: prioritize nearby coins if safe
                if state.nearest_coin_pos is not None:
                    c_dist = next_pos.manhattan_distance(state.nearest_coin_pos)
                    score -= c_dist * 10.0

            # Steering bias towards target (e.g. exit or converter)
            if bias_target is not None:
                t_dist = next_pos.manhattan_distance(bias_target)
                score -= t_dist * 12.0

            if score > best_score:
                best_score = score
                best_act = act

        new_dist = current.move(best_act).manhattan_distance(threat)
        return best_act, curr_dist, new_dist

    def _patrol_safe(
        self,
        current: Position,
        threat: Position,
        legal_actions: List[Action],
        state: State,
    ) -> Action:
        if current.manhattan_distance(threat) <= 2:
            act, _, _ = self._smart_flee(current, threat, legal_actions, state)
            return act

        safe_actions = [
            act for act in legal_actions
            if current.move(act).manhattan_distance(threat) >= 2
        ]
        cand_actions = safe_actions if safe_actions else legal_actions
        if state.nearest_coin_pos is not None:
            return self._best_step_towards(current, state.nearest_coin_pos, cand_actions)
        elif state.nearest_diamond_pos is not None:
            return self._best_step_towards(current, state.nearest_diamond_pos, cand_actions)
        return self.rng.choice(cand_actions)

    def _check_condition_item(self, cond: ConditionItem, state: State) -> bool:
        t = cond.type
        v = cond.value

        if t == "enemy_dist_le":
            return state.enemy_dist <= v
        elif t == "enemy_dist_gt":
            return state.enemy_dist > v
        elif t == "enemy_near":
            return state.enemy_dist <= 2
        elif t == "enemy_adjacent":
            return state.enemy_dist <= 1
        elif t == "enemy_in_los":
            return state.is_enemy_in_line_of_sight()
        elif t == "enemy_blocked":
            return state.is_enemy_blocked_by_wall()
        elif t == "lives_le":
            return state.lives <= v
        elif t == "lives_gt":
            return state.lives > v
        elif t == "steps_gt":
            return state.step_count > v
        elif t == "steps_le":
            return state.step_count <= v
        elif t == "coin_dist_le":
            if state.nearest_coin_pos is None:
                return False
            return state.agent_pos.manhattan_distance(state.nearest_coin_pos) <= v
        elif t == "diamond_dist_le":
            if state.nearest_diamond_pos is None:
                return False
            return state.agent_pos.manhattan_distance(state.nearest_diamond_pos) <= v
        elif t == "converter_dist_le":
            return state.agent_pos.manhattan_distance(state.converter_pos) <= v
        elif t == "exit_dist_le":
            return state.agent_pos.manhattan_distance(state.exit_pos) <= v
        elif t == "has_diamond":
            return state.diamonds_held > 0
        elif t == "one_life":
            return state.lives <= 1
        elif t == "coins_cleared":
            return state.total_coins_remaining == 0
        elif t == "coin_exists":
            return state.nearest_coin_pos is not None
        elif t == "diamond_exists":
            return state.nearest_diamond_pos is not None
        elif t == "always":
            return True
        return False

    def _check_rule(self, rule: IfThenRule, state: State) -> bool:
        """Evaluates conditions with logical AND (all must match)."""
        if not rule.conditions:
            return True
        return all(self._check_condition_item(c, state) for c in rule.conditions)

    def _execute_action_rule(
        self,
        action_name: str,
        state: State,
        legal_actions: List[Action],
    ) -> Tuple[Optional[Action], str]:
        """Executes the rule's action and returns (action, detailed_explanation)."""
        if action_name == "flee_enemy":
            act, c_dist, n_dist = self._smart_flee(state.agent_pos, state.enemy_pos, legal_actions, state, style="balanced")
            if n_dist > c_dist:
                detail = f"فرار هوشمند از هیولا (افزایش فاصله از {c_dist} به {n_dist} خانه)"
            elif n_dist == c_dist:
                detail = f"فرار جانبی و حفظ فاصله امن با هیولا ({c_dist} خانه)"
            else:
                detail = f"تلاش برای گریز تاکتیکی از هیولا (فاصله {n_dist} خانه)"
            return act, detail

        elif action_name == "flee_dodge":
            act, c_dist, n_dist = self._smart_flee(state.agent_pos, state.enemy_pos, legal_actions, state, style="dodge")
            if n_dist > c_dist:
                detail = f"جاخالی تاکتیکی شاه‌دزد و افزایش فاصله از پلیس به {n_dist} خانه"
            elif n_dist == c_dist:
                detail = f"جاخالی تاکتیکی شاه‌دزد به پهلو و شکستن خط دید پلیس (فاصله امن {c_dist} خانه)"
            else:
                detail = f"مانور اضطراری جاخالی شاه‌دزد در بن‌بست (فاصله {n_dist} خانه)"
            return act, detail

        elif action_name == "flee_collect":
            act, c_dist, n_dist = self._smart_flee(state.agent_pos, state.enemy_pos, legal_actions, state, style="collect")
            detail = f"فرار فرصت‌طلبانه (حفظ ایمنی و جمع‌آوری امتیازات در مسیر)"
            return act, detail

        elif action_name == "flee_towards_exit":
            act, c_dist, n_dist = self._smart_flee(
                state.agent_pos, state.enemy_pos, legal_actions, state, bias_target=state.exit_pos
            )
            exit_d = state.agent_pos.move(act).manhattan_distance(state.exit_pos)
            detail = f"فرار هوشمند از پلیس (هیولا) با گرایش به سمت در خروج (فاصله پلیس: {n_dist}، خروج: {exit_d})"
            return act, detail

        elif action_name == "flee_towards_converter":
            act, c_dist, n_dist = self._smart_flee(
                state.agent_pos, state.enemy_pos, legal_actions, state, bias_target=state.converter_pos
            )
            conv_d = state.agent_pos.move(act).manhattan_distance(state.converter_pos)
            detail = f"فرار هوشمند از پلیس (هیولا) به سمت صندوق گنج (مبدل) (فاصله پلیس: {n_dist}، مبدل: {conv_d})"
            return act, detail

        elif action_name == "patrol_safe":
            act = self._patrol_safe(state.agent_pos, state.enemy_pos, legal_actions, state)
            enemy_d = state.agent_pos.move(act).manhattan_distance(state.enemy_pos)
            detail = f"گشت‌زنی امن شاه‌دزد در نقشه دور از پلیس (هیولا) (فاصله کنونی: {enemy_d})"
            return act, detail

        elif action_name == "go_converter":
            act = self._best_step_towards(state.agent_pos, state.converter_pos, legal_actions)
            dist = state.agent_pos.move(act).manhattan_distance(state.converter_pos)
            return act, f"حرکت مستقیم به سمت صندوق گنج (مبدل) جهت باز کردن با کلید (فاصله: {dist})"

        elif action_name == "go_exit":
            act = self._best_step_towards(state.agent_pos, state.exit_pos, legal_actions)
            dist = state.agent_pos.move(act).manhattan_distance(state.exit_pos)
            return act, f"پیش‌روی شاه‌دزد به سمت در خروج و مسیر فرار (فاصله: {dist})"

        elif action_name == "go_nearest_coin":
            if state.nearest_coin_pos is not None:
                act = self._best_step_towards(state.agent_pos, state.nearest_coin_pos, legal_actions)
                dist = state.agent_pos.move(act).manhattan_distance(state.nearest_coin_pos)
                return act, f"حرکت شاه‌دزد به سمت نزدیک‌ترین سکه (فاصله: {dist})"
            return None, "سکه‌ای در نقشه یافت نشد"

        elif action_name == "go_nearest_diamond":
            if state.nearest_diamond_pos is not None:
                act = self._best_step_towards(state.agent_pos, state.nearest_diamond_pos, legal_actions)
                dist = state.agent_pos.move(act).manhattan_distance(state.nearest_diamond_pos)
                return act, f"حرکت شاه‌دزد به سمت نزدیک‌ترین کلید گنج (الماس) (فاصله: {dist})"
            return None, "کلید گنجی در نقشه یافت نشد"

        elif action_name == "random_move":
            return self.rng.choice(legal_actions), "حرکت تصادفی"

        return None, "عمل نامشخص"

    def select_action(self, state: State) -> Tuple[Action, str]:
        legal_actions = self.get_legal_actions(state)
        self.total_steps += 1

        # Check child's If-Then rules in order of priority (1, 2, 3, ...)
        for idx, rule in enumerate(self.strategy.if_then_rules, 1):
            if self._check_rule(rule, state):
                action, detail = self._execute_action_rule(rule.action, state, legal_actions)
                if action is not None:
                    conds_text = " و ".join(format_condition_fa(c) for c in rule.conditions)
                    reason = f"شرط {idx} برقرار شد: اگر [{conds_text}] ➔ {detail}"
                    return action, reason

        # Fallback: No rule matched! Perform random move
        fallback_action = self.rng.choice(legal_actions)
        reason = "هیچ شرطی برای این وضعیت برقرار نشد؛ حرکت تصادفی انجام شد."
        return fallback_action, reason

