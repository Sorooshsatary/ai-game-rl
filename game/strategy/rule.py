"""Child-friendly Strategy definition and If-Then preference rules."""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class IfThenRule:
    """A condition-action rule: IF [condition] THEN [action]."""
    condition: str  # "enemy_near", "has_diamond", "one_life", "coin_exists", "diamond_exists", "coins_cleared", "always"
    action: str     # "flee_enemy", "go_converter", "go_exit", "go_nearest_coin", "go_nearest_diamond", "random_move"

    def to_dict(self) -> Dict[str, str]:
        return {
            "condition": self.condition,
            "action": self.action,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "IfThenRule":
        return cls(
            condition=data.get("condition", "always"),
            action=data.get("action", "random_move"),
        )


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
        IfThenRule(condition="enemy_near", action="flee_enemy"),
        IfThenRule(condition="has_diamond", action="go_converter"),
        IfThenRule(condition="one_life", action="go_exit"),
        IfThenRule(condition="coin_exists", action="go_nearest_coin"),
        IfThenRule(condition="diamond_exists", action="go_nearest_diamond"),
        IfThenRule(condition="coins_cleared", action="go_exit"),
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
                IfThenRule(condition="enemy_near", action="flee_enemy"),
                IfThenRule(condition="has_diamond", action="go_converter"),
                IfThenRule(condition="one_life", action="go_exit"),
                IfThenRule(condition="coin_exists", action="go_nearest_coin"),
                IfThenRule(condition="diamond_exists", action="go_nearest_diamond"),
                IfThenRule(condition="coins_cleared", action="go_exit"),
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
