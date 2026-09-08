"""Child-friendly Strategy definition and preference rules."""

from dataclasses import dataclass, field
from typing import Dict, Any, List


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
    # Core preference sliders (1 to 10 scale for kids)
    coin_priority: float = 7.0         # اهمیت سکه
    diamond_priority: float = 5.0      # اهمیت الماس
    converter_urgency: float = 6.0     # اهمیت بردن الماس به مبدل
    enemy_fear: float = 8.0            # ترس از دشمن و محافظت از جان
    exit_eagerness: float = 5.0        # تمایل به خروج پس از جمع‌آوری

    # Conditional kid-friendly rules
    rules: Dict[str, bool] = field(default_factory=lambda: {
        "flee_adjacent_enemy": True,       # اگر دشمن در خانه مجاور است، حتماً دور شو
        "deposit_before_coins": True,      # اگر الماس داری، اول به مبدل برو
        "diamond_only_if_safe": True,      # فقط زمانی سراغ الماس برو که دشمن دور باشد
        "exit_if_one_life": True,          # اگر ۱ جان مانده، نجات سکه‌ها را اولویت بده
        "exit_if_coins_cleared": True,     # اگر سکه‌ای نمانده، برو به سمت خروج
    })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "coin_priority": self.coin_priority,
            "diamond_priority": self.diamond_priority,
            "converter_urgency": self.converter_urgency,
            "enemy_fear": self.enemy_fear,
            "exit_eagerness": self.exit_eagerness,
            "rules": self.rules,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChildStrategy":
        return cls(
            name=data.get("name", "استراتژی بازیکن"),
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
