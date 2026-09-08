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
        self.assertIn("Reinforcement Learning", res.text)

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

    def test_competition_endpoint(self):
        res = self.client.post("/api/competition")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("leaderboard", data)
        self.assertIn("frames", data)
        self.assertEqual(len(data["leaderboard"]), 4)


if __name__ == "__main__":
    unittest.main()
