"""Unit tests for RuleBasedStrategyAgent with If-Then rules."""

import unittest
from game.strategy.rule import ChildStrategy, IfThenRule
from game.strategy.rule_based_agent import RuleBasedStrategyAgent
from game.environment.state import State
from game.environment.entities import Action, Position


class TestRuleBasedStrategyAgent(unittest.TestCase):
    def setUp(self):
        self.base_state = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(0, 0),
            nearest_coin_pos=Position(4, 2),       # UP
            nearest_diamond_pos=Position(4, 6),    # DOWN
            converter_pos=Position(6, 4),          # RIGHT
            exit_pos=Position(2, 4),               # LEFT
            lives=3,
            coins_held=1,
            diamonds_held=0,
            total_coins_remaining=3,
            grid_width=8,
            grid_height=8,
        )

    def test_emergency_flee_when_monster_near(self):
        strat = ChildStrategy(
            if_then_rules=[
                IfThenRule(condition="enemy_near", action="flee_enemy"),
                IfThenRule(condition="coin_exists", action="go_nearest_coin"),
            ]
        )
        agent = RuleBasedStrategyAgent(strategy=strat)

        state = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(4, 3),  # Enemy is 1 step UP
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
        )

        action, reason = agent.select_action(state)
        self.assertEqual(action, Action.DOWN)
        self.assertIn("هیولا", reason)
        self.assertIn("فرار", reason)

    def test_exit_priority_when_one_life(self):
        strat = ChildStrategy(
            if_then_rules=[
                IfThenRule(condition="one_life", action="go_exit"),
                IfThenRule(condition="coin_exists", action="go_nearest_coin"),
            ]
        )
        agent = RuleBasedStrategyAgent(strategy=strat)

        state = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(7, 7),
            nearest_coin_pos=Position(4, 2),  # UP
            nearest_diamond_pos=None,
            converter_pos=Position(0, 0),
            exit_pos=Position(2, 4),         # LEFT
            lives=1,                         # Only 1 life!
            coins_held=3,
            diamonds_held=0,
            total_coins_remaining=3,
            grid_width=8,
            grid_height=8,
        )

        action, reason = agent.select_action(state)
        self.assertEqual(action, Action.LEFT)
        self.assertIn("خروج", reason)

    def test_converter_when_has_diamond(self):
        strat = ChildStrategy(
            if_then_rules=[
                IfThenRule(condition="has_diamond", action="go_converter"),
                IfThenRule(condition="coin_exists", action="go_nearest_coin"),
            ]
        )
        agent = RuleBasedStrategyAgent(strategy=strat)

        state = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(0, 0),
            nearest_coin_pos=Position(4, 2),  # UP
            nearest_diamond_pos=None,
            converter_pos=Position(6, 4),     # RIGHT
            exit_pos=Position(0, 4),
            lives=3,
            coins_held=0,
            diamonds_held=2,                  # Holding diamonds!
            total_coins_remaining=3,
            grid_width=8,
            grid_height=8,
        )

        action, reason = agent.select_action(state)
        self.assertEqual(action, Action.RIGHT)
        self.assertIn("مبدل", reason)

    def test_fallback_random_move_when_no_condition_met(self):
        # Only rule is for when all coins are cleared, but coins remain
        strat = ChildStrategy(
            if_then_rules=[
                IfThenRule(condition="coins_cleared", action="go_exit"),
            ]
        )
        agent = RuleBasedStrategyAgent(strategy=strat, seed=42)

        state = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(0, 0),
            nearest_coin_pos=Position(4, 2),
            nearest_diamond_pos=None,
            converter_pos=Position(0, 0),
            exit_pos=Position(7, 7),
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=5,  # Coins still remain! Condition is False!
            grid_width=8,
            grid_height=8,
        )

        action, reason = agent.select_action(state)
        self.assertIn(action, [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT])
        self.assertIn("تصادفی", reason)


if __name__ == "__main__":
    unittest.main()
