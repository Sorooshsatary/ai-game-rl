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

    def test_and_compound_conditions(self):
        """Test rule with multiple AND conditions: has_diamond AND enemy_dist_gt 2."""
        from game.strategy.rule import ConditionItem
        strat = ChildStrategy(
            if_then_rules=[
                IfThenRule(
                    conditions=[
                        ConditionItem(type="has_diamond"),
                        ConditionItem(type="enemy_dist_gt", value=2),
                    ],
                    action="go_converter",
                ),
                IfThenRule(condition="always", action="random_move"),
            ]
        )
        agent = RuleBasedStrategyAgent(strategy=strat)

        # Case 1: has diamond, but enemy is CLOSE (dist=1) -> rule should NOT match!
        state_close_enemy = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(4, 3),  # enemy_dist = 1
            nearest_coin_pos=None,
            nearest_diamond_pos=None,
            converter_pos=Position(6, 4),
            exit_pos=Position(0, 0),
            lives=3,
            coins_held=0,
            diamonds_held=1,
            total_coins_remaining=0,
            grid_width=8,
            grid_height=8,
        )
        _, reason1 = agent.select_action(state_close_enemy)
        self.assertIn("تصادفی", reason1)  # Fell through to always -> random_move

        # Case 2: has diamond AND enemy is FAR (dist=4) -> rule SHOULD match!
        state_far_enemy = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(0, 4),  # enemy_dist = 4 > 2
            nearest_coin_pos=None,
            nearest_diamond_pos=None,
            converter_pos=Position(6, 4),
            exit_pos=Position(0, 0),
            lives=3,
            coins_held=0,
            diamonds_held=1,
            total_coins_remaining=0,
            grid_width=8,
            grid_height=8,
        )
        act2, reason2 = agent.select_action(state_far_enemy)
        self.assertEqual(act2, Action.RIGHT)
        self.assertIn("مبدل", reason2)
        self.assertIn("الماس در کوله‌پشتی داری", reason2)
        self.assertIn("محیط امن", reason2)

    def test_distance_threshold_conditions(self):
        """Test coin_dist_le and enemy_dist_le thresholds."""
        from game.strategy.rule import ConditionItem
        strat = ChildStrategy(
            if_then_rules=[
                # Only go to coin if coin_dist <= 2
                IfThenRule(
                    conditions=[ConditionItem(type="coin_dist_le", value=2)],
                    action="go_nearest_coin",
                ),
                IfThenRule(condition="always", action="go_exit"),
            ]
        )
        agent = RuleBasedStrategyAgent(strategy=strat)

        # Coin is distance 4 (> 2) -> should go to exit
        state_far_coin = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(0, 0),
            nearest_coin_pos=Position(4, 0),  # dist = 4
            nearest_diamond_pos=None,
            converter_pos=Position(0, 0),
            exit_pos=Position(0, 4),          # LEFT
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=1,
            grid_width=8,
            grid_height=8,
        )
        act, reason = agent.select_action(state_far_coin)
        self.assertEqual(act, Action.LEFT)
        self.assertIn("خروج", reason)

        # Coin is distance 1 (<= 2) -> should go to coin
        state_near_coin = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(0, 0),
            nearest_coin_pos=Position(4, 3),  # UP, dist = 1
            nearest_diamond_pos=None,
            converter_pos=Position(0, 0),
            exit_pos=Position(0, 4),
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=1,
            grid_width=8,
            grid_height=8,
        )
        act2, reason2 = agent.select_action(state_near_coin)
        self.assertEqual(act2, Action.UP)
        self.assertIn("سکه", reason2)

    def test_smart_flee_explanation_distance(self):
        """Test that fleeing explanation reports distance increase."""
        strat = ChildStrategy(
            if_then_rules=[
                IfThenRule(condition="enemy_near", action="flee_enemy"),
            ]
        )
        agent = RuleBasedStrategyAgent(strategy=strat)
        state = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(4, 3),  # 1 step UP
            nearest_coin_pos=None,
            nearest_diamond_pos=None,
            converter_pos=Position(0, 0),
            exit_pos=Position(7, 7),
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=0,
            grid_width=8,
            grid_height=8,
        )
        act, reason = agent.select_action(state)
        self.assertEqual(act, Action.DOWN)
        self.assertIn("افزایش فاصله از 1 به 2", reason)

    def test_flee_towards_exit(self):
        """Test flee_towards_exit steers fleeing agent towards exit."""
        strat = ChildStrategy(
            if_then_rules=[
                IfThenRule(condition="enemy_near", action="flee_towards_exit"),
            ]
        )
        agent = RuleBasedStrategyAgent(strategy=strat)
        # Enemy is UP (4, 3). Agent is at (4, 4).
        # Fleeing DOWN (4, 5), LEFT (3, 4), or RIGHT (5, 4) all increase distance from enemy.
        # Exit is at (2, 4) (LEFT). Flee towards exit should choose LEFT!
        state = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(4, 3),
            nearest_coin_pos=None,
            nearest_diamond_pos=None,
            converter_pos=Position(7, 7),
            exit_pos=Position(2, 4),  # LEFT
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=0,
            grid_width=8,
            grid_height=8,
        )
        act, reason = agent.select_action(state)
        self.assertEqual(act, Action.LEFT)
        self.assertIn("خروج", reason)

    def test_rule_reordering_priority(self):
        """Test that reordering rules changes decision priority."""
        from game.strategy.rule import ConditionItem
        rule_coin = IfThenRule(conditions=[ConditionItem(type="coin_exists")], action="go_nearest_coin")
        rule_exit = IfThenRule(conditions=[ConditionItem(type="always")], action="go_exit")

        # Order 1: Coin first, then exit
        strat1 = ChildStrategy(if_then_rules=[rule_coin, rule_exit])
        agent1 = RuleBasedStrategyAgent(strategy=strat1)

        # Order 2: Exit first, then coin
        strat2 = ChildStrategy(if_then_rules=[rule_exit, rule_coin])
        agent2 = RuleBasedStrategyAgent(strategy=strat2)

        state = State(
            agent_pos=Position(4, 4),
            enemy_pos=Position(0, 0),
            nearest_coin_pos=Position(4, 2),  # UP
            nearest_diamond_pos=None,
            converter_pos=Position(0, 0),
            exit_pos=Position(2, 4),          # LEFT
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=2,
            grid_width=8,
            grid_height=8,
        )

        act1, _ = agent1.select_action(state)
        self.assertEqual(act1, Action.UP)

        act2, _ = agent2.select_action(state)
        self.assertEqual(act2, Action.LEFT)


if __name__ == "__main__":
    unittest.main()
