"""Unit tests for Authentication, Role-based Access Control, and Admin Management."""

import unittest
from starlette.testclient import TestClient
from game.ui.app import app
from game.database.db import init_db
from game.config import get_active_config, reset_active_config


class TestAuthAndAdmin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def tearDown(self):
        reset_active_config()

    def test_login_success_admin(self):
        res = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("token", data)
        self.assertEqual(data["user"]["role"], "admin")

    def test_login_persian_admin_aliases_and_digits(self):
        # 1. Login with username "admin" and password "123"
        res1 = self.client.post("/api/auth/login", json={"username": "admin", "password": "123"})
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["user"]["role"], "admin")

        # 2. Login with Persian username "ادمین" and Persian digits "۱۲۳"
        res2 = self.client.post("/api/auth/login", json={"username": "ادمین", "password": "۱۲۳"})
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["user"]["role"], "admin")

        # 3. Login with "ادمین ۱۲۳"
        res3 = self.client.post("/api/auth/login", json={"username": "ادمین ۱۲۳", "password": "123"})
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res3.json()["user"]["role"], "admin")

    def test_login_success_student(self):
        res = self.client.post("/api/auth/login", json={"username": "student", "password": "123456"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["role"], "user")

    def test_login_invalid_credentials(self):
        res = self.client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
        self.assertEqual(res.status_code, 401)

    def test_student_forbidden_from_admin_endpoints(self):
        # Login as student
        login_res = self.client.post("/api/auth/login", json={"username": "student", "password": "123456"})
        token = login_res.json()["token"]

        headers = {"Authorization": f"Bearer {token}"}
        # Try getting users
        res = self.client.get("/api/admin/users", headers=headers)
        self.assertEqual(res.status_code, 403)

        # Try getting admin config
        res_cfg = self.client.get("/api/admin/config", headers=headers)
        self.assertEqual(res_cfg.status_code, 403)

    def test_admin_user_crud_operations(self):
        # Login as admin
        admin_token = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).json()["token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. List users
        res_list = self.client.get("/api/admin/users", headers=headers)
        self.assertEqual(res_list.status_code, 200)
        users = res_list.json()["users"]
        self.assertGreaterEqual(len(users), 2)

        # 2. Create new user
        new_username = "test_kid_99"
        res_create = self.client.post("/api/admin/users", json={
            "username": new_username,
            "password": "kidpassword",
            "role": "user"
        }, headers=headers)
        self.assertEqual(res_create.status_code, 200)
        new_user_id = res_create.json()["user"]["id"]

        # 3. Update role to admin
        res_role = self.client.put(f"/api/admin/users/{new_user_id}/role", json={"role": "admin"}, headers=headers)
        self.assertEqual(res_role.status_code, 200)

        # 4. Delete user
        res_del = self.client.delete(f"/api/admin/users/{new_user_id}", headers=headers)
        self.assertEqual(res_del.status_code, 200)

    def test_admin_config_update_and_persistence(self):
        admin_token = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).json()["token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        new_config_payload = {
            "grid_width": 10,
            "grid_height": 10,
            "num_coins": 7,
            "num_diamonds": 3,
            "initial_lives": 4,
            "max_steps": 120,
            "diamond_multiplier": 4,
            "rewards": {
                "coin": 15.0,
                "convert": 25.0,
                "diamond": 1.0,
                "lose_life": -10.0,
                "death": -60.0,
                "exit": 8.0,
                "step": -0.2,
            },
            "rl": {
                "alpha": 0.3,
                "gamma": 0.95,
                "initial_epsilon": 0.9,
                "final_epsilon": 0.08,
                "epsilon_decay": 0.92,
                "episodes": 10,
            }
        }

        # Save config
        res_save = self.client.post("/api/admin/config", json=new_config_payload, headers=headers)
        self.assertEqual(res_save.status_code, 200)
        saved_cfg = res_save.json()["config"]
        self.assertEqual(saved_cfg["grid_width"], 10)
        self.assertEqual(saved_cfg["diamond_multiplier"], 4)
        self.assertEqual(saved_cfg["rewards"]["coin"], 15.0)
        self.assertEqual(saved_cfg["rl"]["initial_epsilon"], 0.9)
        self.assertEqual(saved_cfg["rl"]["final_epsilon"], 0.08)
        self.assertEqual(saved_cfg["rl"]["epsilon_decay"], 0.92)
        self.assertEqual(saved_cfg["rl"]["episodes"], 10)

        # Verify active config in runtime is updated
        active = get_active_config()
        self.assertEqual(active.env.grid_width, 10)
        self.assertEqual(active.env.diamond_to_coin_multiplier, 4)
        self.assertEqual(active.reward.collect_coin, 15.0)
        self.assertEqual(active.rl.initial_epsilon, 0.9)
        self.assertEqual(active.rl.final_epsilon, 0.08)
        self.assertEqual(active.rl.epsilon_decay, 0.92)
        self.assertEqual(active.rl.training_episodes, 10)

        # Verify config.json on disk exists and has the new values
        import json, os
        from game.config import CONFIG_FILE_PATH
        self.assertTrue(os.path.exists(CONFIG_FILE_PATH))
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            disk_cfg = json.load(f)
        self.assertEqual(disk_cfg["rl"]["episodes"], 10)
        self.assertEqual(disk_cfg["rl"]["epsilon_decay"], 0.92)

        # Verify training without explicit episode count uses the config's 10 episodes
        self.client.post("/api/train/reset")
        train_res = self.client.post("/api/train", json={
            "strategy": {
                "name": "Balanced",
                "rules": {
                    "flee_adjacent_enemy": True,
                    "deposit_before_coins": True,
                    "diamond_only_if_safe": True,
                    "exit_if_one_life": True,
                    "exit_if_coins_cleared": True,
                }
            }
        })
        self.assertEqual(train_res.status_code, 200)
        train_data = train_res.json()
        self.assertEqual(train_data["summary"]["total_episodes"], 10)

        # Reset config
        res_reset = self.client.post("/api/admin/config/reset", headers=headers)
        self.assertEqual(res_reset.status_code, 200)
        self.assertEqual(get_active_config().env.grid_width, 8)

    def test_show_presets_admin_flag(self):
        """Verify that show_presets flag is controllable by admin and readable via public config."""
        admin_token = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).json()["token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Check current public config has show_presets field
        cfg_res = self.client.get("/api/config")
        self.assertEqual(cfg_res.status_code, 200)
        self.assertIn("show_presets", cfg_res.json())

        # 2. Update flag to True via admin endpoint
        admin_cfg_res = self.client.get("/api/admin/config", headers=headers)
        self.assertEqual(admin_cfg_res.status_code, 200)
        cfg_data = admin_cfg_res.json()["config"]
        cfg_data["show_presets"] = True

        save_res = self.client.post("/api/admin/config", json=cfg_data, headers=headers)
        self.assertEqual(save_res.status_code, 200)
        self.assertTrue(save_res.json()["config"]["show_presets"])
        self.assertTrue(get_active_config().show_presets)

        # Public config should reflect True
        self.assertTrue(self.client.get("/api/config").json()["show_presets"])

        # 3. Toggle back to False
        cfg_data["show_presets"] = False
        save_res2 = self.client.post("/api/admin/config", json=cfg_data, headers=headers)
        self.assertEqual(save_res2.status_code, 200)
        self.assertFalse(save_res2.json()["config"]["show_presets"])
        self.assertFalse(get_active_config().show_presets)
        self.assertFalse(self.client.get("/api/config").json()["show_presets"])

    def test_show_reward_tuning_admin_flag(self):
        """Verify that show_reward_tuning flag is controllable by admin and readable via public config."""
        admin_token = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).json()["token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Check current public config has show_reward_tuning field
        cfg_res = self.client.get("/api/config")
        self.assertEqual(cfg_res.status_code, 200)
        self.assertIn("show_reward_tuning", cfg_res.json())

        # 2. Update flag to True via admin endpoint
        admin_cfg_res = self.client.get("/api/admin/config", headers=headers)
        self.assertEqual(admin_cfg_res.status_code, 200)
        cfg_data = admin_cfg_res.json()["config"]
        cfg_data["show_reward_tuning"] = True

        save_res = self.client.post("/api/admin/config", json=cfg_data, headers=headers)
        self.assertEqual(save_res.status_code, 200)
        self.assertTrue(save_res.json()["config"]["show_reward_tuning"])
        self.assertTrue(get_active_config().show_reward_tuning)

        # Public config should reflect True
        self.assertTrue(self.client.get("/api/config").json()["show_reward_tuning"])

        # 3. Toggle back to False
        cfg_data["show_reward_tuning"] = False
        save_res2 = self.client.post("/api/admin/config", json=cfg_data, headers=headers)
        self.assertEqual(save_res2.status_code, 200)
        self.assertFalse(save_res2.json()["config"]["show_reward_tuning"])
        self.assertFalse(get_active_config().show_reward_tuning)
        self.assertFalse(self.client.get("/api/config").json()["show_reward_tuning"])

    def test_difficulty_admin_setting(self):
        """Verify that difficulty setting ('easy' vs 'normal') is controllable by admin and readable via public config."""
        admin_token = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).json()["token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Check current public config has difficulty field
        cfg_res = self.client.get("/api/config")
        self.assertEqual(cfg_res.status_code, 200)
        self.assertIn("difficulty", cfg_res.json())

        # 2. Update difficulty to 'easy' via admin endpoint
        admin_cfg_res = self.client.get("/api/admin/config", headers=headers)
        self.assertEqual(admin_cfg_res.status_code, 200)
        cfg_data = admin_cfg_res.json()["config"]
        cfg_data["difficulty"] = "easy"

        save_res = self.client.post("/api/admin/config", json=cfg_data, headers=headers)
        self.assertEqual(save_res.status_code, 200)
        self.assertEqual(save_res.json()["config"]["difficulty"], "easy")
        self.assertEqual(get_active_config().difficulty, "easy")

        # Public config should reflect 'easy'
        self.assertEqual(self.client.get("/api/config").json()["difficulty"], "easy")

        # 3. Toggle back to 'normal'
        cfg_data["difficulty"] = "normal"
        save_res2 = self.client.post("/api/admin/config", json=cfg_data, headers=headers)
        self.assertEqual(save_res2.status_code, 200)
        self.assertEqual(save_res2.json()["config"]["difficulty"], "normal")
        self.assertEqual(get_active_config().difficulty, "normal")
        self.assertEqual(self.client.get("/api/config").json()["difficulty"], "normal")

    def test_custom_rewards_train_and_dual_comparison(self):
        """Verify train and dual comparison endpoints with custom reward shaping parameters."""
        custom_rewards = {
            "exit": 180.0,
            "coin": 2.0,
            "convert": 5.0,
            "lose_life": -50.0,
            "step": -0.5
        }
        strat_payload = {
            "name": "TestStrategy",
            "rules": {
                "flee_adjacent_enemy": True,
                "exit_if_coins_cleared": True
            }
        }

        # Train with custom rewards
        train_res = self.client.post("/api/train", json={
            "strategy": strat_payload,
            "episodes": 2,
            "mode": "hybrid",
            "from_scratch": True,
            "custom_rewards": custom_rewards
        })
        self.assertEqual(train_res.status_code, 200)
        self.assertTrue(train_res.json()["success"])

        # Dual comparison with custom rewards
        dual_res = self.client.post("/api/comparison/dual", json={
            "strategy": strat_payload,
            "seed": 42,
            "custom_rewards": custom_rewards
        })
        self.assertEqual(dual_res.status_code, 200)
        self.assertTrue(dual_res.json()["success"])
        result = dual_res.json()["result"]
        self.assertIn("winner", result)
        self.assertIn("strategy_run", result)
        self.assertIn("rl_run", result)
        self.assertIn("comparison_table", result)


if __name__ == "__main__":
    unittest.main()

