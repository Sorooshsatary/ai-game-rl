"""Unit tests for Multi-Agent Arena and Leaderboard."""

import unittest
from game.config import DEFAULT_CONFIG
from game.strategy.strategy_builder import StrategyBuilder
from game.rl.q_learning import QLearningAgent
from game.competition.arena import MultiAgentArena
from game.competition.leaderboard import Leaderboard


class TestArena(unittest.TestCase):
    def test_multi_agent_match_execution(self):
        presets = StrategyBuilder.get_presets()
        agent1 = QLearningAgent(strategy=presets["balanced"], agent_id="agent1")
        agent2 = QLearningAgent(strategy=presets["coin_hunter"], agent_id="agent2")

        arena = MultiAgentArena(
            config=DEFAULT_CONFIG,
            grid_width=8,
            grid_height=8,
            num_coins=6,
            num_diamonds=2,
            seed=42,
        )

        competitors = [
            ("agent1", "متوازن", "#4CAF50", agent1),
            ("agent2", "شکارچی", "#2196F3", agent2),
        ]

        result = arena.run_match(competitors, max_steps=50)

        self.assertGreater(len(result.frames), 0)
        self.assertEqual(len(result.leaderboard), 2)
        # Leaderboard should have rank 1 and 2
        self.assertEqual(result.leaderboard[0].rank, 1)
        self.assertEqual(result.leaderboard[1].rank, 2)

    def test_leaderboard_ranking_logic(self):
        # Tie-breaker tests
        competitors = [
            {"agent_id": "c1", "coins_exited": 5, "lives": 1, "steps": 40, "has_exited": True, "is_alive": True},
            {"agent_id": "c2", "coins_exited": 10, "lives": 2, "steps": 50, "has_exited": True, "is_alive": True},
            {"agent_id": "c3", "coins_exited": 5, "lives": 3, "steps": 45, "has_exited": True, "is_alive": True},
        ]

        board = Leaderboard.rank_competitors(competitors)
        # c2 should be rank 1 (10 coins)
        self.assertEqual(board[0].agent_id, "c2")
        # c3 should be rank 2 (5 coins, 3 lives beats 5 coins, 1 life)
        self.assertEqual(board[1].agent_id, "c3")
        # c1 should be rank 3
        self.assertEqual(board[2].agent_id, "c1")


if __name__ == "__main__":
    unittest.main()
