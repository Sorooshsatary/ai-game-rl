"""Unit tests for AgentComparisonEngine."""

import unittest
from game.config import DEFAULT_CONFIG
from game.strategy.rule import ChildStrategy
from game.strategy.rule_based_agent import RuleBasedStrategyAgent
from game.rl.q_learning import QLearningAgent
from game.training.comparison import AgentComparisonEngine, DualComparisonResult, AgentRunSummary


class TestAgentComparison(unittest.TestCase):
    def setUp(self):
        self.strat = ChildStrategy(
            name="استراتژی تستی",
            coin_priority=8.0,
            diamond_priority=5.0,
            enemy_fear=8.0,
        )
        self.strat_agent = RuleBasedStrategyAgent(strategy=self.strat, config=DEFAULT_CONFIG)
        self.rl_agent = QLearningAgent(strategy=self.strat, config=DEFAULT_CONFIG, mode="pure")
        self.engine = AgentComparisonEngine(config=DEFAULT_CONFIG)

    def test_run_strategy_agent_only(self):
        summary = self.engine.run_strategy_agent_only(self.strat, seed=12345, max_steps=20)
        self.assertIsInstance(summary, AgentRunSummary)
        self.assertEqual(summary.agent_type, "rule_based")
        self.assertGreater(summary.steps_taken, 0)
        self.assertIn(summary.termination_reason, ["EXIT", "DEATH", "TIMEOUT"])
        self.assertEqual(len(summary.steps), summary.steps_taken)

    def test_run_dual_comparison_identical_seed(self):
        result = self.engine.run_dual_comparison(
            strategy_agent=self.strat_agent,
            rl_agent=self.rl_agent,
            seed=424242,
            max_steps=25,
        )

        self.assertIsInstance(result, DualComparisonResult)
        self.assertEqual(result.seed, 424242)
        self.assertEqual(result.strategy_run.agent_type, "rule_based")
        self.assertEqual(result.rl_run.agent_type, "rl")
        self.assertIn(result.winner, ["rl", "strategy", "tie"])
        self.assertTrue(len(result.analysis_fa) > 0)
        self.assertTrue(len(result.comparison_table) >= 5)

        # Check dictionary serialization
        d = result.to_dict()
        self.assertIn("strategy_run", d)
        self.assertIn("rl_run", d)
        self.assertIn("comparison_table", d)
        self.assertIn("agent_start", d["strategy_run"])
        self.assertIn("enemy_start", d["strategy_run"])

    def test_coin_collection_step_synchronization(self):
        """Verify that agent_pos is updated to the coin tile at the same step the coin is collected."""
        summary = self.engine.run_strategy_agent_only(self.strat, seed=12345, max_steps=50)
        for st in summary.steps:
            if "COLLECT_COIN" in st.events:
                # The collected coin must NOT be present in coins_left at this step
                self.assertNotIn(st.agent_pos, st.coins_left)


if __name__ == "__main__":
    unittest.main()
