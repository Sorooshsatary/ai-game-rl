"""Unit tests for environment entities, grid, enemy, and rules."""

import unittest
from game.config import DEFAULT_CONFIG
from game.environment.entities import Action, Position
from game.environment.grid import GridMap
from game.environment.rules import GameEnvironment


class TestEnvironment(unittest.TestCase):
    def test_position_movement(self):
        p = Position(3, 4)
        self.assertEqual(p.move(Action.UP), Position(3, 3))
        self.assertEqual(p.move(Action.DOWN), Position(3, 5))
        self.assertEqual(p.move(Action.LEFT), Position(2, 4))
        self.assertEqual(p.move(Action.RIGHT), Position(4, 4))
        self.assertEqual(p.manhattan_distance(Position(6, 8)), 3 + 4)

    def test_coin_collection(self):
        # Create controlled environment
        grid = GridMap(
            width=5,
            height=5,
            converter_pos=Position(4, 4),
            exit_pos=Position(0, 4),
            coins={Position(1, 0)},
            diamonds=set(),
        )
        env = GameEnvironment(
            config=DEFAULT_CONFIG,
            grid_map=grid,
            agent_start=Position(0, 0),
            enemy_start=Position(4, 0),
        )

        # Move right onto coin
        res = env.step(Action.RIGHT)
        self.assertEqual(env.agent.position, Position(1, 0))
        self.assertEqual(env.agent.coins, 1)
        self.assertEqual(len(env.grid_map.coins), 0)
        self.assertIn("COLLECT_COIN", res.events)
        self.assertGreater(res.reward, 5.0)  # +10 coin reward - 0.1 step

    def test_diamond_conversion(self):
        grid = GridMap(
            width=5,
            height=5,
            converter_pos=Position(1, 1),
            exit_pos=Position(4, 4),
            coins=set(),
            diamonds={Position(0, 1)},
        )
        env = GameEnvironment(
            config=DEFAULT_CONFIG,
            grid_map=grid,
            agent_start=Position(0, 0),
            enemy_start=Position(4, 0),
        )

        # Step 1: Move DOWN onto diamond
        res1 = env.step(Action.DOWN)
        self.assertEqual(env.agent.diamonds, 1)
        self.assertEqual(env.agent.coins, 0)
        self.assertIn("COLLECT_DIAMOND", res1.events)

        # Step 2: Move RIGHT onto Converter
        res2 = env.step(Action.RIGHT)
        self.assertEqual(env.agent.position, Position(1, 1))
        self.assertEqual(env.agent.diamonds, 0)
        self.assertEqual(env.agent.coins, 2)  # 1 diamond -> 2 coins!
        self.assertIn("CONVERT_DIAMOND_1_TO_2_COINS", "".join(res2.events))

    def test_enemy_hit_and_death(self):
        grid = GridMap(
            width=5,
            height=5,
            converter_pos=Position(4, 4),
            exit_pos=Position(0, 4),
            coins=set(),
            diamonds=set(),
        )
        env = GameEnvironment(
            config=DEFAULT_CONFIG,
            grid_map=grid,
            agent_start=Position(1, 1),
            enemy_start=Position(1, 2),  # adjacent
        )

        initial_lives = env.agent.lives
        # Step into enemy
        res = env.step(Action.DOWN)
        self.assertEqual(env.agent.lives, initial_lives - 1)
        self.assertIn("ENEMY_HIT", res.events)

    def test_exit_success(self):
        grid = GridMap(
            width=5,
            height=5,
            converter_pos=Position(4, 4),
            exit_pos=Position(0, 1),
            coins=set(),
            diamonds=set(),
        )
        env = GameEnvironment(
            config=DEFAULT_CONFIG,
            grid_map=grid,
            agent_start=Position(0, 0),
            enemy_start=Position(4, 4),
        )

        res = env.step(Action.DOWN)
        self.assertTrue(env.agent.has_exited)
        self.assertTrue(res.done)
        self.assertIn("EXIT_SUCCESS", res.events)


if __name__ == "__main__":
    unittest.main()
