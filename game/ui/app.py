"""FastAPI Application serving the Educational RL Game backend and API."""

import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from game.config import DEFAULT_CONFIG
from game.strategy.rule import ChildStrategy
from game.strategy.strategy_builder import StrategyBuilder
from game.training.trainer import Trainer, TrainingResult
from game.rl.q_learning import QLearningAgent
from game.competition.arena import MultiAgentArena

app = FastAPI(title="RL Educational Game", description="Educational & Competitive RL Grid Game for Kids")

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


class TrainRequest(BaseModel):
    strategy: Dict[str, Any]
    episodes: int = 30
    from_scratch: bool = True


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="index.html not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/config")
async def get_config():
    return DEFAULT_CONFIG.to_dict()


@app.get("/api/presets")
async def get_presets():
    return StrategyBuilder.get_preset_list()


@app.post("/api/train")
async def train_agent(req: TrainRequest):
    strat = ChildStrategy.from_dict(req.strategy)
    current_session["strategy"] = strat

    trainer = Trainer(strategy=strat, config=DEFAULT_CONFIG)
    current_session["trainer"] = trainer

    result = trainer.train(num_episodes=req.episodes)
    current_session["last_train_result"] = result
    current_session["player_agent"] = trainer.agent

    return {
        "success": True,
        "summary": result.to_dict(),
    }


@app.post("/api/retrain")
async def retrain_agent(req: TrainRequest):
    if current_session["trainer"] is None:
        return await train_agent(req)

    strat = ChildStrategy.from_dict(req.strategy)
    current_session["strategy"] = strat

    result = current_session["trainer"].retrain_with_new_strategy(
        new_strategy=strat,
        from_scratch=req.from_scratch,
        num_episodes=req.episodes,
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
        raise HTTPException(status_code=404, detail=f"Replay for episode {episode_id} not found")

    replay = trainer.history_replays[episode_id]
    return replay.to_dict()


@app.post("/api/competition")
async def run_competition():
    presets = StrategyBuilder.get_presets()

    # Use trained player agent or train a baseline
    if current_session.get("player_agent") is None:
        default_strat = current_session["strategy"]
        trainer = Trainer(strategy=default_strat, config=DEFAULT_CONFIG)
        trainer.train(num_episodes=20)
        current_session["trainer"] = trainer
        current_session["player_agent"] = trainer.agent

    player_agent = current_session["player_agent"]

    # Pre-train competitor agents
    comp1 = Trainer(strategy=presets["coin_hunter"]).agent
    comp2 = Trainer(strategy=presets["cautious"]).agent
    comp3 = Trainer(strategy=presets["diamond_rusher"]).agent

    Trainer(strategy=presets["coin_hunter"], agent=comp1).train(num_episodes=20)
    Trainer(strategy=presets["cautious"], agent=comp2).train(num_episodes=20)
    Trainer(strategy=presets["diamond_rusher"], agent=comp3).train(num_episodes=20)

    competitors = [
        ("player", f"عامل شما ({player_agent.strategy.name})", "#4CAF50", player_agent),
        ("comp1", "شکارچی سکه (Coin Hunter)", "#2196F3", comp1),
        ("comp2", "محتاط ترسو (Cautious Survivor)", "#FF9800", comp2),
        ("comp3", "عاشق الماس (Diamond Rusher)", "#9C27B0", comp3),
    ]

    arena = MultiAgentArena(
        config=DEFAULT_CONFIG,
        grid_width=10,
        grid_height=10,
        num_coins=8,
        num_diamonds=3,
    )

    match_result = arena.run_match(competitors, max_steps=100)
    return match_result.to_dict()
