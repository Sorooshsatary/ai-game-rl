"""Unit tests for Q-Learning, strategy priors, and policy locking."""

import unittest
from game.config import DEFAULT_CONFIG
from game.environment.entities import Action, Position
from game.environment.state import State
from game.rl.q_learning import QLearningAgent
from game.strategy.rule import ChildStrategy


class TestRL(unittest.TestCase):
    def test_strategy_prior_seeding(self):
        strategy = ChildStrategy(
            name="تست سکه",
            coin_priority=10.0,
            diamond_priority=1.0,
            enemy_fear=5.0,
        )
        agent = QLearningAgent(strategy=strategy, config=DEFAULT_CONFIG)

        # State where coin is to the RIGHT, diamond to the LEFT
        state = State(
            agent_pos=Position(2, 2),
            enemy_pos=Position(7, 7),  # far away
            nearest_coin_pos=Position(4, 2),  # to the RIGHT
            nearest_diamond_pos=Position(0, 2),  # to the LEFT
            converter_pos=Position(0, 0),
            exit_pos=Position(7, 7),
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=5,
            grid_width=8,
            grid_height=8,
        )

        q_vals = agent.get_q_values(state)
        # RIGHT (towards coin) should have strictly higher prior than LEFT (towards diamond)
        self.assertGreater(q_vals[Action.RIGHT], q_vals[Action.LEFT])

    def test_experience_overrides_initial_strategy(self):
        """The core educational test:
        Child says 'Diamond is super important (priority 10)', but moving towards diamond
        leads to enemy damage. RL should learn to decrease Q-value of that action.
        """
        strategy = ChildStrategy(
            name="عاشق الماس بی‌پروا",
            coin_priority=2.0,
            diamond_priority=10.0,
            enemy_fear=2.0,
        )
        agent = QLearningAgent(strategy=strategy, config=DEFAULT_CONFIG)

        state = State(
            agent_pos=Position(2, 2),
            enemy_pos=Position(3, 2),  # Enemy waiting to the RIGHT
            nearest_coin_pos=Position(2, 4),  # Coin is DOWN
            nearest_diamond_pos=Position(4, 2),  # Diamond is to the RIGHT (past enemy)
            converter_pos=Position(0, 0),
            exit_pos=Position(7, 7),
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=3,
            grid_width=8,
            grid_height=8,
        )

        initial_q_right = agent.get_q_values(state)[Action.RIGHT]

        # Simulate negative feedback from enemy hits on action RIGHT
        next_state = State(
            agent_pos=Position(3, 2),
            enemy_pos=Position(3, 2),
            nearest_coin_pos=Position(2, 4),
            nearest_diamond_pos=Position(4, 2),
            converter_pos=Position(0, 0),
            exit_pos=Position(7, 7),
            lives=2,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=3,
            grid_width=8,
            grid_height=8,
        )

        # Update several times with negative reward (-15.0)
        for _ in range(5):
            agent.update(
                state=state,
                action=Action.RIGHT,
                reward=-15.0,
                next_state=next_state,
                done=False,
            )

        updated_q_right = agent.get_q_values(state)[Action.RIGHT]
        self.assertLess(updated_q_right, initial_q_right)

    def test_competition_locking(self):
        strategy = ChildStrategy()
        agent = QLearningAgent(strategy=strategy)

        state = State(
            agent_pos=Position(1, 1),
            enemy_pos=Position(5, 5),
            nearest_coin_pos=Position(2, 1),
            nearest_diamond_pos=None,
            converter_pos=Position(0, 0),
            exit_pos=Position(7, 7),
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=1,
            grid_width=8,
            grid_height=8,
        )

        agent.lock_for_competition()
        self.assertTrue(agent.locked)

        # When locked, updates do not modify Q-values
        q_before = dict(agent.get_q_values(state))
        agent.update(state, Action.RIGHT, reward=100.0, next_state=state, done=True)
        q_after = dict(agent.get_q_values(state))

        self.assertEqual(q_before, q_after)


if __name__ == "__main__":
    unittest.main()
