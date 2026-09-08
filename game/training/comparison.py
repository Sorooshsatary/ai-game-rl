"""Comparison engine running Rule-Based Strategy Agent vs Pure RL Agent on identical environments."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import random

from game.config import GameConfig, DEFAULT_CONFIG
from game.environment.rules import GameEnvironment
from game.environment.entities import Action
from game.strategy.rule import ChildStrategy
from game.strategy.rule_based_agent import RuleBasedStrategyAgent
from game.rl.q_learning import QLearningAgent


@dataclass
class ComparisonStep:
    step_index: int
    agent_pos: List[int]
    enemy_pos: List[int]
    action: str
    action_fa: str
    rule_or_reason: str
    reward: float
    lives: int
    coins: int
    diamonds: int
    events: List[str]
    coins_left: List[List[int]] = field(default_factory=list)
    diamonds_left: List[List[int]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_index": self.step_index,
            "agent_pos": self.agent_pos,
            "enemy_pos": self.enemy_pos,
            "action": self.action,
            "action_fa": self.action_fa,
            "rule_or_reason": self.rule_or_reason,
            "reward": round(self.reward, 1),
            "lives": self.lives,
            "coins": self.coins,
            "diamonds": self.diamonds,
            "events": self.events,
            "coins_left": self.coins_left,
            "diamonds_left": self.diamonds_left,
        }


@dataclass
class AgentRunSummary:
    agent_id: str
    agent_name: str
    agent_type: str  # "rule_based" | "rl"
    total_reward: float
    coins_collected: int
    coins_exited: int
    diamonds_converted: int
    lives_remaining: int
    steps_taken: int
    success: bool
    termination_reason: str
    steps: List[ComparisonStep] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "total_reward": round(self.total_reward, 1),
            "coins_collected": self.coins_collected,
            "coins_exited": self.coins_exited,
            "diamonds_converted": self.diamonds_converted,
            "lives_remaining": self.lives_remaining,
            "steps_taken": self.steps_taken,
            "success": self.success,
            "termination_reason": self.termination_reason,
            "steps": [s.to_dict() for s in self.steps],
        }


@dataclass
class DualComparisonResult:
    seed: int
    map_config: Dict[str, Any]
    strategy_run: AgentRunSummary
    rl_run: AgentRunSummary
    winner: str  # "rl", "strategy", or "tie"
    analysis_fa: str
    comparison_table: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed": self.seed,
            "map_config": self.map_config,
            "strategy_run": self.strategy_run.to_dict(),
            "rl_run": self.rl_run.to_dict(),
            "winner": self.winner,
            "analysis_fa": self.analysis_fa,
            "comparison_table": self.comparison_table,
        }


class AgentComparisonEngine:
    """Runs Rule-Based Strategy Agent and RL Agent on identical randomized maps to compare outcomes."""

    def __init__(self, config: GameConfig = DEFAULT_CONFIG):
        self.config = config

    def run_strategy_agent_only(
        self,
        strategy: ChildStrategy,
        seed: Optional[int] = None,
        max_steps: int = 100,
    ) -> AgentRunSummary:
        """Simulates the child's rule-based agent on a map to inspect behavior and limitations."""
        if seed is None:
            seed = random.randint(1000, 999999)

        env = GameEnvironment(config=self.config, seed=seed)
        agent = RuleBasedStrategyAgent(strategy=strategy, config=self.config)
        return self._execute_agent_run(
            env=env,
            agent=agent,
            agent_id="rule_strategy",
            agent_name=f"استراتژی صلب ({strategy.name})",
            agent_type="rule_based",
            max_steps=max_steps,
        )

    def run_dual_comparison(
        self,
        strategy_agent: RuleBasedStrategyAgent,
        rl_agent: QLearningAgent,
        seed: Optional[int] = None,
        max_steps: int = 100,
    ) -> DualComparisonResult:
        """Runs both agents on identical map and starting seeds, generating direct comparison."""
        if seed is None:
            seed = random.randint(1000, 999999)

        # 1. Run Rule-Based Strategy Agent
        env_strat = GameEnvironment(config=self.config, seed=seed)
        map_config = env_strat.grid_map.to_dict()
        strat_run = self._execute_agent_run(
            env=env_strat,
            agent=strategy_agent,
            agent_id="strategy_agent",
            agent_name=f"عامل استراتژی کودک ({strategy_agent.strategy.name})",
            agent_type="rule_based",
            max_steps=max_steps,
        )

        # 2. Run RL Agent on IDENTICAL seed
        env_rl = GameEnvironment(config=self.config, seed=seed)
        rl_agent.lock_for_competition()  # greedy, no epsilon exploration
        rl_run = self._execute_agent_run(
            env=env_rl,
            agent=rl_agent,
            agent_id="rl_agent",
            agent_name="عامل هوش مصنوعی یادگیرنده",
            agent_type="rl",
            max_steps=max_steps,
        )

        # 3. Determine winner and generate educational analysis
        winner = "tie"
        if rl_run.coins_exited > strat_run.coins_exited:
            winner = "rl"
        elif strat_run.coins_exited > rl_run.coins_exited:
            winner = "strategy"
        else:
            if rl_run.success and not strat_run.success:
                winner = "rl"
            elif strat_run.success and not rl_run.success:
                winner = "strategy"
            elif rl_run.total_reward > strat_run.total_reward:
                winner = "rl"

        # Generate child-friendly Persian explanation of the contrast
        analysis_fa = self._generate_analysis(strat_run, rl_run)

        # Comparison metrics table
        comp_table = [
            {
                "metric": "پایه تصمیم‌گیری",
                "strategy": "قوانین صلب و دستوری شما",
                "rl": "ارزش‌گذاری بر اساس تجربه و پاداش",
            },
            {
                "metric": "خروج موفق از نقشه",
                "strategy": "✅ بله" if strat_run.success else "❌ خیر (مرگ یا اتمام وقت)",
                "rl": "✅ بله" if rl_run.success else "❌ خیر",
            },
            {
                "metric": "سکه‌های ثبت‌شده در پایان",
                "strategy": f"{strat_run.coins_exited} سکه",
                "rl": f"{rl_run.coins_exited} سکه",
            },
            {
                "metric": "الماس‌های تبدیل‌شده",
                "strategy": f"{strat_run.diamonds_converted} الماس",
                "rl": f"{rl_run.diamonds_converted} الماس",
            },
            {
                "metric": "جان باقی‌مانده",
                "strategy": f"{strat_run.lives_remaining} جان",
                "rl": f"{rl_run.lives_remaining} جان",
            },
            {
                "metric": "علت پایان بازی",
                "strategy": self._translate_term(strat_run.termination_reason),
                "rl": self._translate_term(rl_run.termination_reason),
            },
        ]

        return DualComparisonResult(
            seed=seed,
            map_config=map_config,
            strategy_run=strat_run,
            rl_run=rl_run,
            winner=winner,
            analysis_fa=analysis_fa,
            comparison_table=comp_table,
        )

    def _execute_agent_run(
        self,
        env: GameEnvironment,
        agent: Any,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        max_steps: int,
    ) -> AgentRunSummary:
        steps: List[ComparisonStep] = []
        total_reward = 0.0
        initial_diamonds = len(env.grid_map.diamonds)

        step_count = 0
        while not env.done and step_count < max_steps:
            step_count += 1
            curr_state = env.get_state()

            # Action selection
            if agent_type == "rule_based":
                action, reason = agent.select_action(curr_state)
            else:
                action, _, curr_q, _ = agent.select_action(curr_state, epsilon=0.0)
                best_action_q = curr_q.get(action, 0.0)
                reason = f"تجربه هوش مصنوعی: بالاترین ارزش پاداش ({best_action_q:.1f})"

            step_result = env.step(action)
            total_reward += step_result.reward

            step_data = ComparisonStep(
                step_index=step_count,
                agent_pos=[curr_state.agent_pos.x, curr_state.agent_pos.y],
                enemy_pos=[curr_state.enemy_pos.x, curr_state.enemy_pos.y],
                action=action.name,
                action_fa=action.fa_name(),
                rule_or_reason=reason,
                reward=step_result.reward,
                lives=env.agent.lives,
                coins=env.agent.coins,
                diamonds=env.agent.diamonds,
                events=step_result.events,
                coins_left=[[p.x, p.y] for p in env.grid_map.coins],
                diamonds_left=[[p.x, p.y] for p in env.grid_map.diamonds],
            )
            steps.append(step_data)

        coins_exited = env.agent.coins if env.agent.has_exited else 0
        if env.agent.has_exited:
            term_reason = "EXIT"
        elif env.agent.lives <= 0:
            term_reason = "DEATH"
        else:
            term_reason = "TIMEOUT"

        diamonds_converted = max(0, initial_diamonds - len(env.grid_map.diamonds) - env.agent.diamonds)

        return AgentRunSummary(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type,
            total_reward=total_reward,
            coins_collected=env.agent.coins,
            coins_exited=coins_exited,
            diamonds_converted=diamonds_converted,
            lives_remaining=env.agent.lives,
            steps_taken=step_count,
            success=env.agent.has_exited,
            termination_reason=term_reason,
            steps=steps,
        )

    def _generate_analysis(self, strat: AgentRunSummary, rl: AgentRunSummary) -> str:
        if rl.success and not strat.success:
            if strat.termination_reason == "DEATH":
                return (
                    "💡 درس کلیدی: عامل استراتژی صلب به دلیل پایبندی کورکورانه به اولویت‌های اولیه "
                    "(مثل طمع الماس یا عدم تخمین صحیح مسیر هیولا) جان خود را از دست داد و تمام امتیازها سوخت! "
                    "اما عامل یادگیرنده هوش مصنوعی از روی تجارب گذشته یاد گرفته بود که چگونه فاصله ایمن را حفظ کند "
                    "و زنده به خروجی برسد."
                )
            else:
                return (
                    "💡 درس کلیدی: عامل استراتژی صلب نتوانست مسیر بهینه را قبل از اتمام زمان پیدا کند، "
                    "در حالی که هوش مصنوعی مسیرهای منتهی به خروج را کشف کرده و بازی را با موفقیت تمام کرد."
                )
        elif rl.coins_exited > strat.coins_exited:
            return (
                f"💡 درس کلیدی: هر دو عامل زنده خارج شدند، اما هوش مصنوعی با بهینه‌سازی حرکات خود توانست "
                f"{rl.coins_exited - strat.coins_exited} سکه بیشتر ذخیره کند و مسیرهای هوشمندانه‌تری بسازد."
            )
        elif strat.coins_exited > rl.coins_exited:
            return (
                "💡 تحلیل: استراتژی تنظیمی شما در این نقشه خاص عملکرد خیره‌کننده‌ای داشت و حتی هوش مصنوعی را شکست داد! "
                "این نشان می‌دهد قوانین شما پایه‌های بسیار محکمی دارند."
            )
        else:
            return (
                "💡 تحلیل: هر دو عامل عملکرد نزدیکی داشتند؛ این وضعیت زمینه مناسبی است تا با تغییر موقعیت هیولا یا منابع، "
                "انعطاف‌پذیری هوش مصنوعی در برابر قوانین صلب را مجدداً بیازمایید."
            )

    def _translate_term(self, term: str) -> str:
        mapping = {
            "EXIT": "خروج موفق از درب 🚪",
            "DEATH": "کشته شدن توسط هیولا 💀",
            "TIMEOUT": "اتمام حداکثر گام‌ها ⏳",
        }
        return mapping.get(term, term)
