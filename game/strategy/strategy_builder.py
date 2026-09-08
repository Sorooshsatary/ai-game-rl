"""Strategy Builder with kid-friendly presets and configurations."""

from typing import Dict, List, Any
from game.strategy.rule import ChildStrategy


class StrategyBuilder:
    @staticmethod
    def get_presets() -> Dict[str, ChildStrategy]:
        """Returns standard presets suitable for kids and AI competitors in the arena."""
        return {
            "balanced": ChildStrategy(
                name="متوازن هوشمند (Smart Balanced)",
                coin_priority=7.0,
                diamond_priority=6.0,
                converter_urgency=8.0,
                enemy_fear=8.0,
                exit_eagerness=6.0,
                rules={
                    "flee_adjacent_enemy": True,
                    "deposit_before_coins": True,
                    "diamond_only_if_safe": True,
                    "exit_if_one_life": True,
                    "exit_if_coins_cleared": True,
                },
            ),
            "coin_hunter": ChildStrategy(
                name="شکارچی سکه (Coin Hunter)",
                coin_priority=9.5,
                diamond_priority=2.0,
                converter_urgency=3.0,
                enemy_fear=6.0,
                exit_eagerness=7.0,
                rules={
                    "flee_adjacent_enemy": True,
                    "deposit_before_coins": False,
                    "diamond_only_if_safe": False,
                    "exit_if_one_life": True,
                    "exit_if_coins_cleared": True,
                },
            ),
            "diamond_rusher": ChildStrategy(
                name="عاشق الماس (Diamond Rusher)",
                coin_priority=4.0,
                diamond_priority=9.5,
                converter_urgency=9.0,
                enemy_fear=4.0,
                exit_eagerness=4.0,
                rules={
                    "flee_adjacent_enemy": False,
                    "deposit_before_coins": True,
                    "diamond_only_if_safe": False,
                    "exit_if_one_life": False,
                    "exit_if_coins_cleared": True,
                },
            ),
            "cautious": ChildStrategy(
                name="محتاط ترسو (Cautious Survivor)",
                coin_priority=5.0,
                diamond_priority=2.0,
                converter_urgency=5.0,
                enemy_fear=10.0,
                exit_eagerness=9.0,
                rules={
                    "flee_adjacent_enemy": True,
                    "deposit_before_coins": False,
                    "diamond_only_if_safe": True,
                    "exit_if_one_life": True,
                    "exit_if_coins_cleared": True,
                },
            ),
            "daredevil": ChildStrategy(
                name="ماجراجوی نترس (Daredevil)",
                coin_priority=8.0,
                diamond_priority=9.0,
                converter_urgency=8.0,
                enemy_fear=1.5,
                exit_eagerness=3.0,
                rules={
                    "flee_adjacent_enemy": False,
                    "deposit_before_coins": False,
                    "diamond_only_if_safe": False,
                    "exit_if_one_life": False,
                    "exit_if_coins_cleared": True,
                },
            ),
        }

    @classmethod
    def get_preset_list(cls) -> List[Dict[str, Any]]:
        presets = cls.get_presets()
        return [{"id": k, **v.to_dict()} for k, v in presets.items()]
