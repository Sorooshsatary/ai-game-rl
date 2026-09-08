"""Replay data structures and decision inspector for child-friendly analysis."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from game.environment.entities import Action


@dataclass
class DecisionStepLog:
    step_index: int
    state_snapshot: Dict[str, Any]
    prior_q_values: Dict[str, float]
    learned_q_values: Dict[str, float]
    selected_action: str
    selected_action_fa: str
    was_exploratory: bool
    reward: float
    events: List[str]
    explanation_fa: str
    explanation_en: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_index": self.step_index,
            "state_snapshot": self.state_snapshot,
            "prior_q_values": self.prior_q_values,
            "learned_q_values": self.learned_q_values,
            "selected_action": self.selected_action,
            "selected_action_fa": self.selected_action_fa,
            "was_exploratory": self.was_exploratory,
            "reward": round(self.reward, 2),
            "events": self.events,
            "explanation_fa": self.explanation_fa,
            "explanation_en": self.explanation_en,
        }


@dataclass
class EpisodeReplay:
    episode_id: int
    map_config: Dict[str, Any]
    initial_strategy: Dict[str, Any]
    total_reward: float
    coins_exited: int
    coins_collected: int
    diamonds_converted: int
    lives_remaining: int
    steps_taken: int
    success: bool
    termination_reason: str  # "EXIT", "DEATH", "TIMEOUT"
    steps: List[DecisionStepLog] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "map_config": self.map_config,
            "initial_strategy": self.initial_strategy,
            "total_reward": round(self.total_reward, 2),
            "coins_exited": self.coins_exited,
            "coins_collected": self.coins_collected,
            "diamonds_converted": self.diamonds_converted,
            "lives_remaining": self.lives_remaining,
            "steps_taken": self.steps_taken,
            "success": self.success,
            "termination_reason": self.termination_reason,
            "steps": [s.to_dict() for s in self.steps],
        }


def generate_decision_explanation(
    action: Action,
    prior_q: Dict[Action, float],
    learned_q: Dict[Action, float],
    was_exploratory: bool,
    events: List[str],
    state_info: Dict[str, Any],
) -> Tuple[str, str]:
    """Generates an intuitive Persian and English explanation for why this action was chosen."""
    act_str = action.name
    act_fa = action.fa_name()

    if was_exploratory:
        fa = f"عامل در حال کشف مسیرهای جدید بود و حرکت {act_fa} را به صورت تصادفی (Exploration) امتحان کرد."
        en = f"Agent was exploring and randomly tried moving {act_str}."
        return fa, en

    # Check if learned Q diverged from prior
    prior_best_act = max(prior_q, key=prior_q.get)
    learned_best_act = max(learned_q, key=learned_q.get)

    enemy_dist = state_info.get("distances", {}).get("enemy", 999)
    diamonds_held = state_info.get("diamonds_held", 0)

    if prior_best_act != learned_best_act and learned_best_act == action:
        # Divergence! The core educational takeaway!
        fa = (
            f"تجربه نظر استراتژی اولیه را تغییر داد! استراتژی اولیه حرکت {prior_best_act.name} را پیشنهاد می‌داد، "
            f"اما هوش مصنوعی با یادگیری ارزش واقعی حرکت {act_fa} (امتیاز {learned_q[action]:.1f}) را برتر دانست."
        )
        en = (
            f"Experience overridden initial strategy! The strategy preferred {prior_best_act.name}, "
            f"but RL learned that {act_str} (Q={learned_q[action]:.1f}) is safer/more rewarding."
        )
    elif "ENEMY_HIT" in events or enemy_dist <= 2:
        fa = f"به دلیل حضور دشمن در نزدیکی، عامل حرکت محافظه‌کارانه {act_fa} را برگزید تا جانش حفظ شود."
        en = f"Due to nearby enemy threat, agent chose defensive move {act_str}."
    elif diamonds_held > 0 and "CONVERT" in "".join(events):
        fa = f"عامل الماس‌ها را با موفقیت به مبدل رساند و آن‌ها را به سکه تبدیل کرد!"
        en = f"Agent brought diamonds to Converter and transformed them into coins!"
    elif "COLLECT_COIN" in events:
        fa = f"عامل با موفقیت یک سکه با ارزش برداشت (+۱۰ پاداش)."
        en = f"Agent successfully collected a coin (+10 reward)."
    else:
        fa = f"بر اساس ترکیب استراتژی اولیه و یادگیری (Q={learned_q[action]:.1f})، حرکت به سمت {act_fa} انتخاب شد."
        en = f"Based on strategy prior and learning (Q={learned_q[action]:.1f}), move {act_str} was selected."

    return fa, en
