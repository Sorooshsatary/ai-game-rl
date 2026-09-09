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
        agent = QLearningAgent(strategy=strategy, config=DEFAULT_CONFIG, mode="hybrid")

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

    def test_pure_rl_mode_initializes_to_zero(self):
        """In pure RL mode, agent starts completely un-opinionated (Q=0.0)."""
        agent = QLearningAgent(mode="pure")
        state = State(
            agent_pos=Position(2, 2),
            enemy_pos=Position(7, 7),
            nearest_coin_pos=Position(4, 2),
            nearest_diamond_pos=Position(0, 2),
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
        for act in Action:
            self.assertEqual(q_vals[act], 0.0)

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
        agent = QLearningAgent(strategy=strategy, config=DEFAULT_CONFIG, mode="hybrid")

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

    def test_boundary_action_masking_prevents_wall_bumps(self):
        """When agent is at grid edge (x=7 on 8x8 grid), Action.RIGHT is illegal
        and must never be selected, even if it has the highest Q-value.
        """
        agent = QLearningAgent(mode="pure")
        state = State(
            agent_pos=Position(7, 3),
            enemy_pos=Position(0, 0),
            nearest_coin_pos=Position(6, 3),
            nearest_diamond_pos=None,
            converter_pos=Position(0, 0),
            exit_pos=Position(0, 7),
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=1,
            grid_width=8,
            grid_height=8,
        )

        legal_acts = state.get_legal_actions()
        self.assertNotIn(Action.RIGHT, legal_acts)
        self.assertIn(Action.LEFT, legal_acts)
        self.assertIn(Action.UP, legal_acts)
        self.assertIn(Action.DOWN, legal_acts)

        # Force Action.RIGHT to have an artificially high Q-value
        discrete = state.to_discrete()
        agent.q_table[discrete] = {
            Action.RIGHT: 999.0,  # Illegal bump into wall
            Action.LEFT: 10.0,
            Action.UP: 5.0,
            Action.DOWN: 2.0,
        }

        # Greedy choice must NOT pick RIGHT despite Q=999.0
        chosen_action, was_exploratory, _, _ = agent.select_action(state, epsilon=0.0)
        self.assertEqual(chosen_action, Action.LEFT)

    def test_exploration_never_chooses_illegal_boundary_actions(self):
        """Even during 100% exploration (epsilon=1.0), illegal moves are never chosen."""
        agent = QLearningAgent(mode="pure")
        # Corner position (0, 0): only DOWN and RIGHT are legal
        corner_state = State(
            agent_pos=Position(0, 0),
            enemy_pos=Position(7, 7),
            nearest_coin_pos=None,
            nearest_diamond_pos=None,
            converter_pos=Position(7, 0),
            exit_pos=Position(7, 7),
            lives=3,
            coins_held=0,
            diamonds_held=0,
            total_coins_remaining=0,
            grid_width=8,
            grid_height=8,
        )

        for _ in range(50):
            action, was_exp, _, _ = agent.select_action(corner_state, epsilon=1.0)
            self.assertTrue(was_exp)
            self.assertIn(action, [Action.DOWN, Action.RIGHT])
            self.assertNotIn(action, [Action.UP, Action.LEFT])

    def test_internal_walls_are_masked(self):
        """State with internal walls masks actions moving into wall positions."""
        state = State(
            agent_pos=Position(2, 2),
            enemy_pos=Position(7, 7),
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
            walls={Position(3, 2)},  # Wall immediately to the RIGHT
        )
        legal = state.get_legal_actions()
        self.assertNotIn(Action.RIGHT, legal)
        self.assertIn(Action.LEFT, legal)
        self.assertIn(Action.UP, legal)
        self.assertIn(Action.DOWN, legal)

    def test_state_includes_direction_and_heading(self):
        """Verify that agent_heading and enemy_heading are present in to_discrete and to_dict."""
        state = State(
            agent_pos=Position(2, 2),
            enemy_pos=Position(7, 7),
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
            agent_heading=Action.UP,
            enemy_heading=Action.LEFT,
        )
        discrete = state.to_discrete()
        self.assertEqual(len(discrete), 9)
        self.assertEqual(discrete[8], "UP")  # agent_dir
        st_dict = state.to_dict()
        self.assertEqual(st_dict["agent_heading"], "UP")
        self.assertEqual(st_dict["enemy_heading"], "LEFT")

    def test_enemy_heading_threat_distinction(self):
        """Verify that enemy moving towards agent produces different discrete state than enemy moving away."""
        state_approaching = State(
            agent_pos=Position(2, 2),
            enemy_pos=Position(4, 2),  # dist 2, RIGHT
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
            agent_heading=Action.RIGHT,
            enemy_heading=Action.LEFT,  # Enemy is moving LEFT, towards agent!
        )

        state_receding = State(
            agent_pos=Position(2, 2),
            enemy_pos=Position(4, 2),  # dist 2, RIGHT
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
            agent_heading=Action.RIGHT,
            enemy_heading=Action.RIGHT,  # Enemy is moving RIGHT, away from agent!
        )

        disc_app = state_approaching.to_discrete()
        disc_rec = state_receding.to_discrete()

        # Threat at index 4 must distinguish between heading LEFT vs heading RIGHT
        self.assertIn("DANGER_RIGHT_LEFT", disc_app[4])
        self.assertIn("DANGER_RIGHT_RIGHT", disc_rec[4])
        self.assertNotEqual(disc_app, disc_rec)

    def test_heading_updates_on_environment_step(self):
        """Verify that GameEnvironment updates agent.heading and state heading upon taking action."""
        from game.environment.rules import GameEnvironment
        env = GameEnvironment(seed=123)
        res1 = env.step(Action.UP)
        self.assertEqual(env.agent.heading, Action.UP)
        self.assertEqual(res1.next_state.agent_heading, Action.UP)

        res2 = env.step(Action.LEFT)
        self.assertEqual(env.agent.heading, Action.LEFT)
        self.assertEqual(res2.next_state.agent_heading, Action.LEFT)


if __name__ == "__main__":
    unittest.main()
