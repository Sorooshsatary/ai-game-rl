"""Leaderboard and scoring evaluation for the competition."""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class LeaderboardEntry:
    rank: int
    agent_id: str
    agent_name: str
    strategy_name: str
    coins_exited: int
    lives_remaining: int
    steps_taken: int
    is_alive: bool
    has_exited: bool
    status_fa: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "strategy_name": self.strategy_name,
            "coins_exited": self.coins_exited,
            "lives": self.lives_remaining,
            "steps": self.steps_taken,
            "is_alive": self.is_alive,
            "has_exited": self.has_exited,
            "status_fa": self.status_fa,
        }


class Leaderboard:
    @staticmethod
    def rank_competitors(results: List[Dict[str, Any]]) -> List[LeaderboardEntry]:
        """Ranks competitors based on:
        1. Coins successfully exited (Primary metric)
        2. Remaining lives (Tie-breaker 1)
        3. Fewer steps / faster time (Tie-breaker 2)
        """
        # Sort key: (-coins_exited, -lives, steps_taken)
        sorted_results = sorted(
            results,
            key=lambda r: (
                -r.get("coins_exited", 0),
                -r.get("lives", 0),
                r.get("steps", 999),
            ),
        )

        entries = []
        for idx, r in enumerate(sorted_results, 1):
            if r.get("has_exited", False):
                status_fa = "خروج موفق با پیروزی 🏆"
            elif not r.get("is_alive", True):
                status_fa = "کشته شد توسط دشمن 💀"
            else:
                status_fa = "اتمام زمان بازی ⏳"

            entries.append(
                LeaderboardEntry(
                    rank=idx,
                    agent_id=r["agent_id"],
                    agent_name=r.get("agent_name", r["agent_id"]),
                    strategy_name=r.get("strategy_name", "نامشخص"),
                    coins_exited=r.get("coins_exited", 0),
                    lives_remaining=r.get("lives", 0),
                    steps_taken=r.get("steps", 0),
                    is_alive=r.get("is_alive", True),
                    has_exited=r.get("has_exited", False),
                    status_fa=status_fa,
                )
            )
        return entries
