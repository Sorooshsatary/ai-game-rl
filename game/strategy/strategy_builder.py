"""Strategy Builder with kid-friendly presets and configurations."""

from typing import Dict, List, Any
from game.strategy.rule import ChildStrategy, IfThenRule, ConditionItem


class StrategyBuilder:
    @staticmethod
    def get_default_strategy() -> ChildStrategy:
        """Returns the default naive/weak strategy (greedy coin collector that does NOT flee from police)."""
        return ChildStrategy(
            name="شاه‌دزد ساده‌لوح (پیش‌فرض)",
            if_then_rules=[
                IfThenRule(conditions=[ConditionItem(type="has_diamond")], action="go_converter"),
                IfThenRule(conditions=[ConditionItem(type="coin_exists")], action="go_nearest_coin"),
            ],
            default_action="random_move",
            coin_priority=8.0,
            diamond_priority=5.0,
            converter_urgency=6.0,
            enemy_fear=1.0,
            exit_eagerness=2.0,
        )

    @staticmethod
    def get_extra_presets() -> Dict[str, ChildStrategy]:
        """Returns extra high-performance tactical strategies for admin injection."""
        return {
            "phantom_tactician": ChildStrategy(
                name="شاه‌دزد شبح (تاکتیکال و فرار)",
                if_then_rules=[
                    IfThenRule(conditions=[ConditionItem(type="enemy_adjacent")], action="flee_dodge"),
                    IfThenRule(conditions=[ConditionItem(type="one_life")], action="flee_towards_exit"),
                    IfThenRule(conditions=[ConditionItem(type="enemy_dist_le", value=2)], action="flee_dodge"),
                    IfThenRule(conditions=[ConditionItem(type="steps_gt", value=28)], action="go_exit"),
                    IfThenRule(conditions=[ConditionItem(type="has_diamond")], action="go_converter"),
                    IfThenRule(conditions=[ConditionItem(type="diamond_exists")], action="go_nearest_diamond"),
                    IfThenRule(conditions=[ConditionItem(type="coin_exists")], action="go_nearest_coin"),
                ],
                default_action="random_move",
                coin_priority=7.5,
                diamond_priority=8.0,
                converter_urgency=9.0,
                enemy_fear=8.5,
                exit_eagerness=7.0,
            ),
            "speed_runner": ChildStrategy(
                name="شاه‌دزد زمان‌بند (مدیریت گام‌ها)",
                if_then_rules=[
                    IfThenRule(conditions=[ConditionItem(type="enemy_adjacent")], action="flee_dodge"),
                    IfThenRule(conditions=[ConditionItem(type="steps_gt", value=25)], action="go_exit"),
                    IfThenRule(conditions=[ConditionItem(type="has_diamond")], action="go_converter"),
                    IfThenRule(conditions=[ConditionItem(type="steps_le", value=15)], action="go_nearest_coin"),
                    IfThenRule(conditions=[ConditionItem(type="diamond_exists")], action="go_nearest_diamond"),
                    IfThenRule(conditions=[ConditionItem(type="coin_exists")], action="go_nearest_coin"),
                ],
                default_action="random_move",
                coin_priority=8.5,
                diamond_priority=7.0,
                converter_urgency=8.5,
                enemy_fear=6.5,
                exit_eagerness=9.5,
            ),
            "treasure_master": ChildStrategy(
                name="شاه‌دزد کلکسیونر گنج (صندوق و الماس)",
                if_then_rules=[
                    IfThenRule(conditions=[ConditionItem(type="enemy_adjacent")], action="flee_dodge"),
                    IfThenRule(conditions=[ConditionItem(type="one_life")], action="go_exit"),
                    IfThenRule(conditions=[ConditionItem(type="has_diamond")], action="go_converter"),
                    IfThenRule(conditions=[ConditionItem(type="diamond_exists")], action="go_nearest_diamond"),
                    IfThenRule(conditions=[ConditionItem(type="coin_dist_le", value=2)], action="go_nearest_coin"),
                    IfThenRule(conditions=[ConditionItem(type="enemy_dist_le", value=2)], action="flee_towards_exit"),
                    IfThenRule(conditions=[ConditionItem(type="coin_exists")], action="go_nearest_coin"),
                ],
                default_action="random_move",
                coin_priority=6.0,
                diamond_priority=10.0,
                converter_urgency=10.0,
                enemy_fear=7.0,
                exit_eagerness=6.0,
            ),
            "ninja_survivor": ChildStrategy(
                name="شاه‌دزد نینجا (استاد بقا و خروج)",
                if_then_rules=[
                    IfThenRule(conditions=[ConditionItem(type="enemy_adjacent")], action="flee_dodge"),
                    IfThenRule(conditions=[ConditionItem(type="enemy_dist_le", value=2)], action="flee_towards_exit"),
                    IfThenRule(conditions=[ConditionItem(type="one_life")], action="go_exit"),
                    IfThenRule(conditions=[ConditionItem(type="has_diamond")], action="go_converter"),
                    IfThenRule(conditions=[ConditionItem(type="coins_cleared")], action="go_exit"),
                    IfThenRule(conditions=[ConditionItem(type="coin_exists")], action="go_nearest_coin"),
                    IfThenRule(conditions=[ConditionItem(type="diamond_exists")], action="go_nearest_diamond"),
                ],
                default_action="random_move",
                coin_priority=7.0,
                diamond_priority=6.0,
                converter_urgency=7.5,
                enemy_fear=9.5,
                exit_eagerness=9.0,
            ),
        }

    @classmethod
    def get_presets(cls, include_extra: bool = False) -> Dict[str, ChildStrategy]:
        """Returns standard presets, optionally including extra advanced strategies."""
        presets = {
            "balanced": ChildStrategy(
                name="شاه‌دزد متوازن و هوشمند",
                if_then_rules=[
                    IfThenRule(conditions=[ConditionItem(type="enemy_adjacent")], action="flee_dodge"),
                    IfThenRule(conditions=[ConditionItem(type="has_diamond")], action="go_converter"),
                    IfThenRule(conditions=[ConditionItem(type="coin_exists")], action="go_nearest_coin"),
                ],
                default_action="random_move",
                coin_priority=7.0,
                diamond_priority=6.0,
                converter_urgency=8.0,
                enemy_fear=6.0,
                exit_eagerness=6.0,
            ),
            "coin_hunter": ChildStrategy(
                name="شاه‌دزد سکه‌ربا",
                if_then_rules=[
                    IfThenRule(conditions=[ConditionItem(type="enemy_adjacent")], action="flee_dodge"),
                    IfThenRule(conditions=[ConditionItem(type="coin_exists")], action="go_nearest_coin"),
                ],
                default_action="random_move",
                coin_priority=9.5,
                diamond_priority=2.0,
                converter_urgency=3.0,
                enemy_fear=6.0,
                exit_eagerness=7.0,
            ),
            "diamond_rusher": ChildStrategy(
                name="شاه‌دزد شکارچی گنج",
                if_then_rules=[
                    IfThenRule(conditions=[ConditionItem(type="has_diamond")], action="go_converter"),
                    IfThenRule(conditions=[ConditionItem(type="diamond_exists")], action="go_nearest_diamond"),
                ],
                default_action="random_move",
                coin_priority=4.0,
                diamond_priority=9.5,
                converter_urgency=9.0,
                enemy_fear=4.0,
                exit_eagerness=4.0,
            ),
            "cautious": ChildStrategy(
                name="شاه‌دزد محتاط و فراری",
                if_then_rules=[
                    IfThenRule(conditions=[ConditionItem(type="enemy_dist_le", value=2)], action="flee_towards_exit"),
                    IfThenRule(conditions=[ConditionItem(type="coin_exists")], action="go_nearest_coin"),
                ],
                default_action="random_move",
                coin_priority=5.0,
                diamond_priority=2.0,
                converter_urgency=5.0,
                enemy_fear=10.0,
                exit_eagerness=9.0,
            ),
            "daredevil": ChildStrategy(
                name="شاه‌دزد نترس و جسور",
                if_then_rules=[
                    IfThenRule(conditions=[ConditionItem(type="has_diamond")], action="go_converter"),
                    IfThenRule(conditions=[ConditionItem(type="coin_exists")], action="go_nearest_coin"),
                ],
                default_action="random_move",
                coin_priority=8.0,
                diamond_priority=9.0,
                converter_urgency=8.0,
                enemy_fear=1.5,
                exit_eagerness=3.0,
            ),
        }
        if include_extra:
            presets.update(cls.get_extra_presets())
        return presets

    @classmethod
    def get_preset_list(cls, include_extra: bool = False) -> List[Dict[str, Any]]:
        base_presets = cls.get_presets(include_extra=False)
        result = [{"id": k, "is_extra": False, **v.to_dict()} for k, v in base_presets.items()]
        if include_extra:
            extra_presets = cls.get_extra_presets()
            for k, v in extra_presets.items():
                result.append({"id": k, "is_extra": True, **v.to_dict()})
        return result

