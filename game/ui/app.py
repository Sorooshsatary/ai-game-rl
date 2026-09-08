"""FastAPI Application serving the Educational RL Game backend, API, Auth, and Admin Panel."""

import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from game.config import (
    DEFAULT_CONFIG,
    get_active_config,
    set_active_config,
    reset_active_config,
    GameConfig,
)
from game.database.db import (
    init_db,
    get_user_by_username,
    create_user,
    list_users,
    update_user_role,
    delete_user,
    create_session,
    delete_session,
    verify_password,
    authenticate_user,
)
from game.auth.auth_manager import (
    get_current_user,
    require_authenticated_user,
    require_admin,
    extract_token_from_request,
)
from game.environment.rules import GameEnvironment
from game.strategy.rule import ChildStrategy
from game.strategy.strategy_builder import StrategyBuilder
from game.strategy.rule_based_agent import RuleBasedStrategyAgent
from game.training.trainer import Trainer, TrainingResult
from game.training.comparison import AgentComparisonEngine
from game.rl.q_learning import QLearningAgent
from game.competition.arena import MultiAgentArena

app = FastAPI(
    title="بازی آموزشی هوش مصنوعی",
    description="بستر آموزشی و رقابتی یادگیری تقویتی و عامل‌های قانون‌محور",
)

# Initialize database schema and default users
init_db()

# Global state for active session
current_session = {
    "strategy": StrategyBuilder.get_presets()["balanced"],
    "trainer": None,
    "last_train_result": None,
    "player_agent": None,
}

# Mount static and templates directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# =========================================================================
# Request Schemas
# =========================================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "user"  # "admin" or "user"


class UpdateRoleRequest(BaseModel):
    role: str  # "admin" or "user"


class TrainRequest(BaseModel):
    strategy: Dict[str, Any]
    episodes: Optional[int] = None
    from_scratch: bool = False
    mode: str = "hybrid"  # "pure" or "hybrid"


class StrategyTestRequest(BaseModel):
    strategy: Dict[str, Any]
    seed: Optional[int] = None


class DualComparisonRequest(BaseModel):
    strategy: Dict[str, Any]
    seed: Optional[int] = None


class SystemConfigRequest(BaseModel):
    grid_width: int = Field(8, ge=5, le=16)
    grid_height: int = Field(8, ge=5, le=16)
    num_coins: int = Field(5, ge=1, le=20)
    num_diamonds: int = Field(2, ge=0, le=10)
    initial_lives: int = Field(3, ge=1, le=10)
    max_steps: int = Field(100, ge=20, le=500)
    diamond_multiplier: int = Field(2, ge=1, le=50)
    show_presets: bool = False
    rewards: Dict[str, float]
    rl: Dict[str, Any]


# =========================================================================
# Core Page & Configuration Endpoints
# =========================================================================

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="صفحه مورد نظر یافت نشد")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/config")
async def get_config():
    return get_active_config().to_dict()


@app.get("/api/presets")
async def get_presets():
    return StrategyBuilder.get_preset_list()


# =========================================================================
# Authentication Endpoints
# =========================================================================

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="نام کاربری یا رمز عبور اشتباه است.")

    token = create_session(user["id"])
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "created_at": user["created_at"],
        }
    }


@app.post("/api/auth/logout")
async def logout(request: Request):
    token = extract_token_from_request(request)
    if token:
        delete_session(token)
    return {"success": True, "message": "خروج موفقیت‌آمیز بود."}


@app.get("/api/auth/me")
async def get_me(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    if current_user:
        return {
            "authenticated": True,
            "user": {
                "id": current_user["id"],
                "username": current_user["username"],
                "role": current_user["role"],
                "created_at": current_user["created_at"],
            }
        }
    return {"authenticated": False, "user": None}


# =========================================================================
# Admin Management Endpoints (Admin Only)
# =========================================================================

@app.get("/api/admin/users")
async def admin_list_users(admin: Dict[str, Any] = Depends(require_admin)):
    return {
        "success": True,
        "users": list_users()
    }


@app.post("/api/admin/users")
async def admin_create_user(req: CreateUserRequest, admin: Dict[str, Any] = Depends(require_admin)):
    username = req.username.strip()
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="نام کاربری باید حداقل ۳ کاراکتر باشد.")
    if len(req.password) < 4:
        raise HTTPException(status_code=400, detail="رمز عبور باید حداقل ۴ کاراکتر باشد.")
    if req.role not in ("admin", "user"):
        raise HTTPException(status_code=400, detail="نقش کاربری نامعتبر است (تنها admin یا user مجاز است).")

    existing = get_user_by_username(username)
    if existing:
        raise HTTPException(status_code=400, detail="این نام کاربری قبلاً ثبت شده است.")

    new_user = create_user(username, req.password, req.role)
    return {
        "success": True,
        "message": f"کاربر {username} با موفقیت ایجاد شد.",
        "user": new_user
    }


@app.put("/api/admin/users/{user_id}/role")
async def admin_update_user_role(user_id: int, req: UpdateRoleRequest, admin: Dict[str, Any] = Depends(require_admin)):
    if req.role not in ("admin", "user"):
        raise HTTPException(status_code=400, detail="سطح دسترسی نامعتبر است.")
    if admin["id"] == user_id and req.role != "admin":
        raise HTTPException(status_code=400, detail="امکان سلب دسترسی مدیریت از حساب خودتان وجود ندارد.")

    success = update_user_role(user_id, req.role)
    if not success:
        raise HTTPException(status_code=404, detail="کاربر مورد نظر یافت نشد.")
    return {"success": True, "message": "سطح دسترسی کاربر با موفقیت تغییر یافت."}


@app.delete("/api/admin/users/{user_id}")
async def admin_delete_user(user_id: int, admin: Dict[str, Any] = Depends(require_admin)):
    if admin["id"] == user_id:
        raise HTTPException(status_code=400, detail="نمی‌توانید حساب کاربری خودتان را حذف کنید.")

    success = delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="کاربر مورد نظر پیدا نشد.")
    return {"success": True, "message": "کاربر با موفقیت حذف شد."}


@app.get("/api/admin/config")
async def admin_get_config(admin: Dict[str, Any] = Depends(require_admin)):
    return {
        "success": True,
        "config": get_active_config().to_dict()
    }


@app.post("/api/admin/config")
async def admin_save_config(req: SystemConfigRequest, admin: Dict[str, Any] = Depends(require_admin)):
    new_cfg = GameConfig.from_dict(req.model_dump())
    saved = set_active_config(new_cfg)
    if current_session.get("trainer"):
        current_session["trainer"].config = saved
        current_session["trainer"].env = GameEnvironment(config=saved)
        current_session["trainer"].agent.config = saved
    return {
        "success": True,
        "message": "تنظیمات بازی و یادگیری تقویتی با موفقیت ذخیره و در فایل کانفیگ اعمال شد.",
        "config": saved.to_dict()
    }


@app.post("/api/admin/config/reset")
async def admin_reset_config(admin: Dict[str, Any] = Depends(require_admin)):
    cfg = reset_active_config()
    if current_session.get("trainer"):
        current_session["trainer"].config = cfg
        current_session["trainer"].env = GameEnvironment(config=cfg)
        current_session["trainer"].agent.config = cfg
    return {
        "success": True,
        "message": "تنظیمات با موفقیت به مقادیر اولیه کارخانه بازگردانده و در فایل کانفیگ ذخیره شد.",
        "config": cfg.to_dict()
    }


# =========================================================================
# Game Simulation & Training Endpoints (Using Active Config)
# =========================================================================

@app.post("/api/strategy/test")
async def test_strategy_endpoint(req: StrategyTestRequest):
    active_cfg = get_active_config()
    strat = ChildStrategy.from_dict(req.strategy)
    engine = AgentComparisonEngine(config=active_cfg)
    seed = req.seed or 12345
    env_map = GameEnvironment(config=active_cfg, seed=seed)
    run_summary = engine.run_strategy_agent_only(strat, seed=seed)
    map_dict = env_map.grid_map.to_dict()
    map_dict["agent_start"] = [env_map.agent_start.x, env_map.agent_start.y]
    map_dict["enemy_start"] = [env_map.enemy_start.x, env_map.enemy_start.y]
    return {
        "success": True,
        "seed": seed,
        "map_config": map_dict,
        "summary": run_summary.to_dict(),
    }


@app.post("/api/comparison/dual")
async def dual_comparison_endpoint(req: DualComparisonRequest):
    active_cfg = get_active_config()
    strat = ChildStrategy.from_dict(req.strategy)
    current_session["strategy"] = strat

    # Ensure trained RL agent (if not yet trained or 0 completed episodes, train baseline)
    trainer = current_session.get("trainer")
    if trainer is None or trainer.total_episodes_completed == 0:
        trainer = Trainer(strategy=strat, config=active_cfg, mode="hybrid")
        trainer.train(num_episodes=max(30, active_cfg.rl.training_episodes))
        current_session["trainer"] = trainer
        current_session["player_agent"] = trainer.agent
    else:
        current_session["player_agent"] = trainer.agent

    strat_agent = RuleBasedStrategyAgent(strategy=strat, config=active_cfg)
    rl_agent = current_session["player_agent"]

    engine = AgentComparisonEngine(config=active_cfg)
    comparison_res = engine.run_dual_comparison(
        strategy_agent=strat_agent,
        rl_agent=rl_agent,
        seed=req.seed,
        episodes_trained=trainer.total_episodes_completed,
    )
    return {
        "success": True,
        "result": comparison_res.to_dict(),
    }


@app.post("/api/train")
async def train_agent(req: TrainRequest):
    active_cfg = get_active_config()
    strat = ChildStrategy.from_dict(req.strategy)
    current_session["strategy"] = strat

    trainer = current_session.get("trainer")
    # If no trainer exists, or mode changed, or explicitly requested from_scratch
    if trainer is None or trainer.mode != req.mode or req.from_scratch:
        trainer = Trainer(strategy=strat, config=active_cfg, mode=req.mode)
        current_session["trainer"] = trainer
    else:
        trainer.config = active_cfg
        trainer.strategy = strat

    episodes = req.episodes if (req.episodes is not None and req.episodes > 0) else active_cfg.rl.training_episodes
    result = trainer.train(num_episodes=episodes)
    current_session["last_train_result"] = result
    current_session["player_agent"] = trainer.agent

    return {
        "success": True,
        "summary": result.to_dict(),
    }


@app.post("/api/train/reset")
async def reset_training_agent():
    if current_session.get("trainer"):
        current_session["trainer"].reset()
        current_session["player_agent"] = current_session["trainer"].agent
        current_session["last_train_result"] = None
    else:
        current_session["player_agent"] = None
        current_session["last_train_result"] = None
        current_session["trainer"] = None
    return {
        "success": True,
        "message": "حافظه یادگیری و تجربیات هوش مصنوعی با موفقیت بازنشانی شد.",
    }


@app.post("/api/retrain")
async def retrain_agent(req: TrainRequest):
    active_cfg = get_active_config()
    if current_session["trainer"] is None:
        return await train_agent(req)

    strat = ChildStrategy.from_dict(req.strategy)
    current_session["strategy"] = strat

    episodes = req.episodes if (req.episodes is not None and req.episodes > 0) else active_cfg.rl.retrain_episodes
    result = current_session["trainer"].retrain_with_new_strategy(
        new_strategy=strat,
        from_scratch=req.from_scratch,
        num_episodes=episodes,
    )
    current_session["last_train_result"] = result
    current_session["player_agent"] = current_session["trainer"].agent

    return {
        "success": True,
        "summary": result.to_dict(),
    }


@app.get("/api/replay/{episode_id}")
async def get_replay(episode_id: int):
    trainer = current_session.get("trainer")
    if not trainer or episode_id not in trainer.history_replays:
        raise HTTPException(status_code=404, detail=f"اپیزود {episode_id} پیدا نشد.")

    replay = trainer.history_replays[episode_id]
    return replay.to_dict()


@app.post("/api/competition")
async def run_competition():
    active_cfg = get_active_config()
    presets = StrategyBuilder.get_presets()

    if current_session.get("player_agent") is None:
        default_strat = current_session["strategy"]
        trainer = Trainer(strategy=default_strat, config=active_cfg)
        trainer.train(num_episodes=20)
        current_session["trainer"] = trainer
        current_session["player_agent"] = trainer.agent

    player_agent = current_session["player_agent"]

    comp1 = Trainer(strategy=presets["coin_hunter"], config=active_cfg).agent
    comp2 = Trainer(strategy=presets["cautious"], config=active_cfg).agent
    comp3 = Trainer(strategy=presets["diamond_rusher"], config=active_cfg).agent

    Trainer(strategy=presets["coin_hunter"], agent=comp1, config=active_cfg).train(num_episodes=20)
    Trainer(strategy=presets["cautious"], agent=comp2, config=active_cfg).train(num_episodes=20)
    Trainer(strategy=presets["diamond_rusher"], agent=comp3, config=active_cfg).train(num_episodes=20)

    competitors = [
        ("player", f"عامل شما ({player_agent.strategy.name})", "#4CAF50", player_agent),
        ("comp1", "شکارچی سکه", "#2196F3", comp1),
        ("comp2", "محتاط و هوشیار", "#FF9800", comp2),
        ("comp3", "عاشق الماس", "#9C27B0", comp3),
    ]

    arena = MultiAgentArena(
        config=active_cfg,
        grid_width=10,
        grid_height=10,
        num_coins=8,
        num_diamonds=3,
    )

    match_result = arena.run_match(competitors, max_steps=100)
    return match_result.to_dict()
