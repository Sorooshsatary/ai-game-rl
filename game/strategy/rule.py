"""Child-friendly Strategy definition and If-Then preference rules."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class ConditionItem:
    """A single atomic condition, with an optional numeric value (e.g. distance threshold)."""
    type: str = "always"
    value: int = 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data: Any) -> "ConditionItem":
        if isinstance(data, str):
            # Backward compatibility with legacy string condition names
            if data == "enemy_near":
                return cls(type="enemy_dist_le", value=2)
            elif data == "enemy_adjacent":
                return cls(type="enemy_dist_le", value=1)
            return cls(type=data, value=2)
        if isinstance(data, dict):
            return cls(
                type=data.get("type", "always"),
                value=int(data.get("value", 2)),
            )
        return cls(type="always", value=2)


class IfThenRule:
    """A condition-action rule: IF [condition(s)] THEN [action].
    Multiple conditions are evaluated with logical AND (all must match).
    """

    def __init__(
        self,
        condition: Optional[str] = None,
        action: str = "random_move",
        conditions: Optional[List[ConditionItem]] = None,
    ):
        self.action = action
        if conditions is not None and len(conditions) > 0:
            self.conditions = conditions
        elif condition is not None:
            self.conditions = [ConditionItem.from_dict(condition)]
        else:
            self.conditions = [ConditionItem(type="always", value=2)]

    @property
    def condition(self) -> str:
        return self.conditions[0].type if self.conditions else "always"

    @condition.setter
    def condition(self, val: str):
        if self.conditions:
            self.conditions[0].type = val
        else:
            self.conditions = [ConditionItem.from_dict(val)]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "condition": self.condition,
            "conditions": [c.to_dict() for c in self.conditions],
            "action": self.action,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IfThenRule":
        action = data.get("action", "random_move")
        raw_conds = data.get("conditions")
        if raw_conds and isinstance(raw_conds, list):
            conds = [ConditionItem.from_dict(c) for c in raw_conds]
        elif "condition" in data:
            conds = [ConditionItem.from_dict(data["condition"])]
        else:
            conds = [ConditionItem(type="always", value=2)]
        return cls(action=action, conditions=conds)


@dataclass
class StrategyRule:
    rule_id: str
    name_fa: str
    name_en: str
    description_fa: str
    description_en: str
    enabled: bool = True
    weight_modifier: float = 1.0


@dataclass
class ChildStrategy:
    name: str = "استراتژی من"

    # Block-based If-Then Rules (checked sequentially from top to bottom)
    if_then_rules: List[IfThenRule] = field(default_factory=lambda: [
        IfThenRule(conditions=[ConditionItem(type="enemy_dist_le", value=2)], action="flee_enemy"),
        IfThenRule(conditions=[ConditionItem(type="has_diamond")], action="go_converter"),
        IfThenRule(conditions=[ConditionItem(type="one_life")], action="go_exit"),
        IfThenRule(conditions=[ConditionItem(type="coin_exists")], action="go_nearest_coin"),
        IfThenRule(conditions=[ConditionItem(type="diamond_exists")], action="go_nearest_diamond"),
        IfThenRule(conditions=[ConditionItem(type="coins_cleared")], action="go_exit"),
    ])

    # Default fallback action if no condition matches
    default_action: str = "random_move"

    # Numerical preference weights (kept for backward-compatibility with prior computation)
    coin_priority: float = 7.0
    diamond_priority: float = 5.0
    converter_urgency: float = 6.0
    enemy_fear: float = 8.0
    exit_eagerness: float = 5.0
    rules: Dict[str, bool] = field(default_factory=lambda: {
        "flee_adjacent_enemy": True,
        "deposit_before_coins": True,
        "diamond_only_if_safe": True,
        "exit_if_one_life": True,
        "exit_if_coins_cleared": True,
    })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "if_then_rules": [r.to_dict() for r in self.if_then_rules],
            "default_action": self.default_action,
            "coin_priority": self.coin_priority,
            "diamond_priority": self.diamond_priority,
            "converter_urgency": self.converter_urgency,
            "enemy_fear": self.enemy_fear,
            "exit_eagerness": self.exit_eagerness,
            "rules": self.rules,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChildStrategy":
        raw_rules = data.get("if_then_rules", [])
        if raw_rules:
            parsed_rules = [IfThenRule.from_dict(r) for r in raw_rules]
        else:
            parsed_rules = [
                IfThenRule(conditions=[ConditionItem(type="enemy_dist_le", value=2)], action="flee_enemy"),
                IfThenRule(conditions=[ConditionItem(type="has_diamond")], action="go_converter"),
                IfThenRule(conditions=[ConditionItem(type="one_life")], action="go_exit"),
                IfThenRule(conditions=[ConditionItem(type="coin_exists")], action="go_nearest_coin"),
                IfThenRule(conditions=[ConditionItem(type="diamond_exists")], action="go_nearest_diamond"),
                IfThenRule(conditions=[ConditionItem(type="coins_cleared")], action="go_exit"),
            ]

        return cls(
            name=data.get("name", "استراتژی بازیکن"),
            if_then_rules=parsed_rules,
            default_action=data.get("default_action", "random_move"),
            coin_priority=float(data.get("coin_priority", 7.0)),
            diamond_priority=float(data.get("diamond_priority", 5.0)),
            converter_urgency=float(data.get("converter_urgency", 6.0)),
            enemy_fear=float(data.get("enemy_fear", 8.0)),
            exit_eagerness=float(data.get("exit_eagerness", 5.0)),
            rules=data.get("rules", {
                "flee_adjacent_enemy": True,
                "deposit_before_coins": True,
                "diamond_only_if_safe": True,
                "exit_if_one_life": True,
                "exit_if_coins_cleared": True,
            }),
        )
