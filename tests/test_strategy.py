"""Unit tests for Strategy presets and Prior Engine."""

import unittest
from game.strategy.rule import ChildStrategy
from game.strategy.strategy_builder import StrategyBuilder
from game.strategy.strategy_to_prior import StrategyPriorEngine
from game.environment.state import State
from game.environment.entities import Action, Position


class TestStrategy(unittest.TestCase):
    def test_presets_exist(self):
        presets = StrategyBuilder.get_presets()
        self.assertIn("balanced", presets)
        self.assertIn("coin_hunter", presets)
        self.assertIn("diamond_rusher", presets)
        self.assertIn("cautious", presets)
        self.assertIn("daredevil", presets)

        for name, strat in presets.items():
            self.assertIsInstance(strat, ChildStrategy)
            self.assertGreater(strat.coin_priority, 0)
            self.assertGreater(strat.enemy_fear, 0)

    def test_prior_divergence_between_strategies(self):
        strat_coin = ChildStrategy(coin_priority=10.0, diamond_priority=1.0)
        strat_diamond = ChildStrategy(coin_priority=1.0, diamond_priority=10.0)

        engine_coin = StrategyPriorEngine(strat_coin)
        engine_diamond = StrategyPriorEngine(strat_diamond)

        # State: Coin is UP, Diamond is DOWN
        state = State(
            agent_pos=Position(3, 3),
            enemy_pos=Position(7, 7),
            nearest_coin_pos=Position(3, 1),      # UP
            nearest_diamond_pos=Position(3, 5),   # DOWN
            converter_pos=Position(0, 0),
            exit_pos=Position(7, 7),
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=4,
            grid_width=8,
            grid_height=8,
        )

        priors_coin = engine_coin.compute_all_priors(state)
        priors_diamond = engine_diamond.compute_all_priors(state)

        # Coin lover prefers UP
        self.assertGreater(priors_coin[Action.UP][0], priors_coin[Action.DOWN][0])
        # Diamond lover prefers DOWN
        self.assertGreater(priors_diamond[Action.DOWN][0], priors_diamond[Action.UP][0])


    def test_extra_presets(self):
        """Test that extra presets exist and include_extra toggle works."""
        extra = StrategyBuilder.get_extra_presets()
        self.assertIn("phantom_tactician", extra)
        self.assertIn("speed_runner", extra)
        self.assertIn("treasure_master", extra)
        self.assertIn("ninja_survivor", extra)

        for name, strat in extra.items():
            self.assertIsInstance(strat, ChildStrategy)
            self.assertGreater(len(strat.if_then_rules), 0)

        # get_presets default should have 5
        base_presets = StrategyBuilder.get_presets(include_extra=False)
        self.assertEqual(len(base_presets), 5)

        # get_presets(include_extra=True) should have 9
        all_presets = StrategyBuilder.get_presets(include_extra=True)
        self.assertEqual(len(all_presets), 9)

        # get_preset_list with include_extra
        preset_list_base = StrategyBuilder.get_preset_list(include_extra=False)
        self.assertEqual(len(preset_list_base), 5)
        self.assertTrue(all(p["is_extra"] is False for p in preset_list_base))

        preset_list_all = StrategyBuilder.get_preset_list(include_extra=True)
        self.assertEqual(len(preset_list_all), 9)
        extra_count = sum(1 for p in preset_list_all if p["is_extra"])
        self.assertEqual(extra_count, 4)

    def test_extra_presets_behavior(self):
        """Test that extra presets produce valid and intended actions in state scenarios."""
        from game.strategy.rule_based_agent import RuleBasedStrategyAgent

        extra = StrategyBuilder.get_extra_presets()

        # 1. phantom_tactician: adjacent enemy -> flee_dodge
        phantom_agent = RuleBasedStrategyAgent(strategy=extra["phantom_tactician"])
        state_danger = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(4, 5),  # adjacent
            nearest_coin_pos=Position(4, 2),
            nearest_diamond_pos=None,
            converter_pos=Position(0, 0),
            exit_pos=Position(7, 7),
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=3,
            grid_width=8,
            grid_height=8,
            step_count=5,
        )
        act_phantom, reason_phantom = phantom_agent.select_action(state_danger)
        self.assertIn("جاخالی", reason_phantom)

        # 2. speed_runner: steps > 25 -> go_exit
        speed_agent = RuleBasedStrategyAgent(strategy=extra["speed_runner"])
        state_late_game = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(0, 0),  # far
            nearest_coin_pos=Position(4, 2),  # UP
            nearest_diamond_pos=None,
            converter_pos=Position(0, 0),
            exit_pos=Position(2, 4),          # LEFT
            lives=3,
            coins_held=2,
            diamonds_held=0,
            total_coins_remaining=3,
            grid_width=8,
            grid_height=8,
            step_count=30,  # > 25 -> rush to exit!
        )
        act_speed, reason_speed = speed_agent.select_action(state_late_game)
        self.assertEqual(act_speed, Action.LEFT)
        self.assertIn("خروج", reason_speed)


if __name__ == "__main__":
    unittest.main()

