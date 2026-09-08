"""Unit tests for FastAPI endpoints."""

import unittest
from starlette.testclient import TestClient
from game.ui.app import app


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_index_page(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers["content-type"])
        self.assertIn("یادگیری تقویتی", res.text)

    def test_presets_endpoint(self):
        res = self.client.get("/api/presets")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 4)

    def test_train_and_replay_endpoints(self):
        payload = {
            "strategy": {
                "name": "تست API",
                "coin_priority": 8.0,
                "diamond_priority": 4.0,
                "converter_urgency": 7.0,
                "enemy_fear": 8.0,
                "exit_eagerness": 6.0,
                "rules": {
                    "flee_adjacent_enemy": True,
                    "deposit_before_coins": True,
                    "diamond_only_if_safe": True,
                    "exit_if_one_life": True,
                    "exit_if_coins_cleared": True,
                },
            },
            "episodes": 5,
        }
        train_res = self.client.post("/api/train", json=payload)
        self.assertEqual(train_res.status_code, 200)
        train_data = train_res.json()
        self.assertTrue(train_data["success"])
        self.assertIn("summary", train_data)

        # Test replay endpoint
        available_episodes = train_data["summary"]["available_replay_episodes"]
        self.assertGreater(len(available_episodes), 0)
        replay_id = available_episodes[0]

        rep_res = self.client.get(f"/api/replay/{replay_id}")
        self.assertEqual(rep_res.status_code, 200)
        replay_data = rep_res.json()
        self.assertEqual(replay_data["episode_id"], replay_id)
        self.assertIn("steps", replay_data)

    def test_strategy_test_endpoint(self):
        payload = {
            "strategy": {
                "name": "تست استراتژی قانون‌محور",
                "coin_priority": 9.0,
                "diamond_priority": 2.0,
                "converter_urgency": 5.0,
                "enemy_fear": 8.0,
                "exit_eagerness": 6.0,
                "rules": {
                    "flee_adjacent_enemy": True,
                    "deposit_before_coins": True,
                    "diamond_only_if_safe": True,
                    "exit_if_one_life": True,
                    "exit_if_coins_cleared": True,
                },
            },
            "seed": 9999,
        }
        res = self.client.post("/api/strategy/test", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("summary", data)
        self.assertEqual(data["summary"]["agent_type"], "rule_based")

    def test_dual_comparison_endpoint(self):
        payload = {
            "strategy": {
                "name": "استراتژی مقایسه",
                "coin_priority": 7.0,
                "diamond_priority": 6.0,
                "converter_urgency": 7.0,
                "enemy_fear": 8.0,
                "exit_eagerness": 5.0,
                "rules": {
                    "flee_adjacent_enemy": True,
                    "deposit_before_coins": True,
                    "diamond_only_if_safe": True,
                    "exit_if_one_life": True,
                    "exit_if_coins_cleared": True,
                },
            },
            "seed": 8888,
        }
        res = self.client.post("/api/comparison/dual", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("result", data)
        self.assertIn("strategy_run", data["result"])
        self.assertIn("rl_run", data["result"])
        self.assertIn("analysis_fa", data["result"])

    def test_cumulative_training_and_reset(self):
        payload = {
            "strategy": {"name": "test_cum", "if_then_rules": []},
            "episodes": 10,
        }
        # 1. Reset first to ensure clean state
        self.client.post("/api/train/reset")

        # 2. First training session (10 episodes)
        res1 = self.client.post("/api/train", json=payload).json()
        self.assertEqual(res1["summary"]["total_episodes"], 10)
        self.assertEqual(len(res1["summary"]["metrics"]), 10)

        # 3. Second training session continues from previous (10 more -> 20 total)
        res2 = self.client.post("/api/train", json=payload).json()
        self.assertEqual(res2["summary"]["total_episodes"], 20)
        self.assertEqual(len(res2["summary"]["metrics"]), 20)

        # 4. Reset training
        res_reset = self.client.post("/api/train/reset").json()
        self.assertTrue(res_reset["success"])

        # 5. Third training session starts from 0 again (10 episodes)
        res3 = self.client.post("/api/train", json=payload).json()
        self.assertEqual(res3["summary"]["total_episodes"], 10)
        self.assertEqual(len(res3["summary"]["metrics"]), 10)


if __name__ == "__main__":
    unittest.main()

