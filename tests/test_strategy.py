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


if __name__ == "__main__":
    unittest.main()
