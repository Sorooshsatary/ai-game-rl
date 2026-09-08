"""Strategy Builder with kid-friendly presets and configurations."""

from typing import Dict, List, Any
from game.strategy.rule import ChildStrategy, IfThenRule


class StrategyBuilder:
    @staticmethod
    def get_presets() -> Dict[str, ChildStrategy]:
        """Returns standard presets suitable for kids and AI competitors in the arena."""
        return {
            "balanced": ChildStrategy(
                name="متوازن و هوشمند",
                if_then_rules=[
                    IfThenRule(condition="enemy_near", action="flee_enemy"),
                    IfThenRule(condition="has_diamond", action="go_converter"),
                    IfThenRule(condition="one_life", action="go_exit"),
                    IfThenRule(condition="coin_exists", action="go_nearest_coin"),
                    IfThenRule(condition="diamond_exists", action="go_nearest_diamond"),
                    IfThenRule(condition="coins_cleared", action="go_exit"),
                ],
                default_action="random_move",
                coin_priority=7.0,
                diamond_priority=6.0,
                converter_urgency=8.0,
                enemy_fear=8.0,
                exit_eagerness=6.0,
            ),
            "coin_hunter": ChildStrategy(
                name="شکارچی سکه",
                if_then_rules=[
                    IfThenRule(condition="enemy_adjacent", action="flee_enemy"),
                    IfThenRule(condition="coin_exists", action="go_nearest_coin"),
                    IfThenRule(condition="coins_cleared", action="go_exit"),
                ],
                default_action="random_move",
                coin_priority=9.5,
                diamond_priority=2.0,
                converter_urgency=3.0,
                enemy_fear=6.0,
                exit_eagerness=7.0,
            ),
            "diamond_rusher": ChildStrategy(
                name="عاشق الماس",
                if_then_rules=[
                    IfThenRule(condition="has_diamond", action="go_converter"),
                    IfThenRule(condition="diamond_exists", action="go_nearest_diamond"),
                    IfThenRule(condition="coin_exists", action="go_nearest_coin"),
                    IfThenRule(condition="coins_cleared", action="go_exit"),
                ],
                default_action="random_move",
                coin_priority=4.0,
                diamond_priority=9.5,
                converter_urgency=9.0,
                enemy_fear=4.0,
                exit_eagerness=4.0,
            ),
            "cautious": ChildStrategy(
                name="محتاط و هوشیار",
                if_then_rules=[
                    IfThenRule(condition="enemy_near", action="flee_enemy"),
                    IfThenRule(condition="one_life", action="go_exit"),
                    IfThenRule(condition="coin_exists", action="go_nearest_coin"),
                    IfThenRule(condition="coins_cleared", action="go_exit"),
                ],
                default_action="random_move",
                coin_priority=5.0,
                diamond_priority=2.0,
                converter_urgency=5.0,
                enemy_fear=10.0,
                exit_eagerness=9.0,
            ),
            "daredevil": ChildStrategy(
                name="ماجراجوی نترس",
                if_then_rules=[
                    IfThenRule(condition="diamond_exists", action="go_nearest_diamond"),
                    IfThenRule(condition="has_diamond", action="go_converter"),
                    IfThenRule(condition="coin_exists", action="go_nearest_coin"),
                ],
                default_action="random_move",
                coin_priority=8.0,
                diamond_priority=9.0,
                converter_urgency=8.0,
                enemy_fear=1.5,
                exit_eagerness=3.0,
            ),
        }

    @classmethod
    def get_preset_list(cls) -> List[Dict[str, Any]]:
        presets = cls.get_presets()
        return [{"id": k, **v.to_dict()} for k, v in presets.items()]
