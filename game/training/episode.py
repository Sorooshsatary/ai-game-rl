"""Single episode execution and step recording."""

from typing import Optional
from game.environment.rules import GameEnvironment
from game.environment.entities import Action
from game.rl.q_learning import QLearningAgent
from game.replay.replay import DecisionStepLog, EpisodeReplay, generate_decision_explanation


def run_episode(
    env: GameEnvironment,
    agent: QLearningAgent,
    epsilon: float,
    episode_id: int,
    seed: Optional[int] = None,
) -> EpisodeReplay:
    """Executes a full episode on a randomized map and records detailed replay logs."""
    state = env.reset(new_map=True, seed=seed)
    if hasattr(agent, "reset_history"):
        agent.reset_history()
    map_config = env.grid_map.to_dict()
    map_config["agent_start"] = [env.agent_start.x, env.agent_start.y]
    map_config["enemy_start"] = [env.enemy_start.x, env.enemy_start.y]

    steps = []
    total_reward = 0.0
    initial_coins_count = len(env.grid_map.coins)
    initial_diamonds_count = len(env.grid_map.diamonds)

    step_idx = 0
    while not env.done:
        step_idx += 1
        curr_state = env.get_state()
        state_snapshot_before = curr_state.to_dict()

        # Agent chooses action
        action, was_exploratory, curr_q, prior_q = agent.select_action(curr_state, epsilon)

        # Environment step
        step_result = env.step(action)
        total_reward += step_result.reward

        # Agent learns
        agent.update(
            state=curr_state,
            action=action,
            reward=step_result.reward,
            next_state=step_result.next_state,
            done=step_result.done,
        )

        # Generate educational explanation
        exp_fa, exp_en = generate_decision_explanation(
            action=action,
            prior_q=prior_q,
            learned_q=agent.get_q_values(curr_state),
            was_exploratory=was_exploratory,
            events=step_result.events,
            state_info=state_snapshot_before,
        )

        step_log = DecisionStepLog(
            step_index=step_idx,
            state_snapshot=step_result.next_state.to_dict(),
            prior_q_values={a.name: val for a, val in prior_q.items()},
            learned_q_values={a.name: val for a, val in agent.get_q_values(curr_state).items()},
            selected_action=action.name,
            selected_action_fa=action.fa_name(),
            was_exploratory=was_exploratory,
            reward=step_result.reward,
            events=step_result.events,
            explanation_fa=exp_fa,
            explanation_en=exp_en,
        )
        steps.append(step_log)

    coins_exited = env.agent.coins if env.agent.has_exited else 0
    if env.agent.has_exited:
        term_reason = "EXIT"
    elif env.agent.lives <= 0:
        term_reason = "DEATH"
    else:
        term_reason = "TIMEOUT"

    return EpisodeReplay(
        episode_id=episode_id,
        map_config=map_config,
        initial_strategy=agent.strategy.to_dict(),
        total_reward=total_reward,
        coins_exited=coins_exited,
        coins_collected=env.agent.coins,
        diamonds_converted=(initial_diamonds_count - len(env.grid_map.diamonds) - env.agent.diamonds),
        lives_remaining=env.agent.lives,
        steps_taken=step_idx,
        success=env.agent.has_exited,
        termination_reason=term_reason,
        steps=steps,
    )
