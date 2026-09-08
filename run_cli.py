import sys

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from game.config import DEFAULT_CONFIG
from game.strategy.strategy_builder import StrategyBuilder
from game.training.trainer import Trainer
from game.competition.arena import MultiAgentArena


def print_banner(text: str):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def main():
    print_banner("🎮 بازی آموزشی و رقابتی Reinforcement Learning 🎮")
    print("مفهوم کلیدی: کودک استراتژی اولیه را تعیین می‌کند؛ RL مسیر و تصمیمات را یاد می‌گیرد.\n")

    # Step 1: Strategy Design
    print_banner("مرحله ۱: انتخاب یا طراحی استراتژی اولیه")
    presets = StrategyBuilder.get_presets()
    print("استراتژی‌های در دسترس:")
    for k, strat in presets.items():
        print(f"  - [{k}] {strat.name}: اولویت سکه={strat.coin_priority}, الماس={strat.diamond_priority}, ترس از دشمن={strat.enemy_fear}")

    # Pick Balanced or Daredevil for fun
    chosen_strat = presets["balanced"]
    print(f"\nاستراتژی انتخابی: {chosen_strat.name}")

    # Step 2: Training
    print_banner("مرحله ۲: آموزش ۳۰ اپیزود روی نقشه‌های تصادفی")
    trainer = Trainer(strategy=chosen_strat, config=DEFAULT_CONFIG)

    def on_progress(ep, total, metric):
        if ep % 5 == 0 or ep == 1:
            res_str = "موفق (خروج) ✅" if metric.success else f"شکست ({metric.termination_reason}) ❌"
            print(f"اپیزود {ep:02d}/{total} | اپسیلون: {metric.epsilon:.2f} | پاداش: {metric.total_reward:6.1f} | سکه‌های خروجی: {metric.coins_exited} | نتیجه: {res_str}")

    train_result = trainer.train(num_episodes=30, progress_callback=on_progress)

    print(f"\nنتایج آموزش:")
    print(f"  - نرخ موفقیت در ۵ اپیزود آخر: {train_result.final_success_rate * 100:.0f}%")
    print(f"  - میانگین پاداش در ۵ اپیزود آخر: {train_result.avg_reward_last_5:.1f}")
    print(f"  - تعداد وضعیت‌هایی که تجربه هوش مصنوعی نظر اولیه استراتژی را اصلاح کرد: {train_result.strategy_divergence_count}")

    # Step 3: Replay Inspection
    print_banner("مرحله ۳: تحلیل بازپخش (Replay) و چرایی تصمیمات عامل")
    sample_ep = list(train_result.replays.keys())[-1]
    replay = train_result.replays[sample_ep]
    print(f"بررسی اپیزود شماره {sample_ep}:")
    print(f"  - تعداد کل گام‌ها: {replay.steps_taken}")
    print(f"  - وضعیت پایان: {replay.termination_reason}")
    print(f"  - سکه‌های خارج شده: {replay.coins_exited}")

    print("\nنمونه‌ای از تحلیل تصمیمات در گام‌های کلیدی:")
    for step in replay.steps[:6]:
        print(f"  [گام {step.step_index:02d}] حرکت انتخابی: {step.selected_action_fa} ({step.selected_action})")
        print(f"     مقادیر اولیه استراتژی: {step.prior_q_values}")
        print(f"     مقادیر یادگرفته‌شده Q: {step.learned_q_values}")
        print(f"     توضیح برای کودک: {step.explanation_fa}")
        if step.events:
            print(f"     رویدادها: {', '.join(step.events)}")
        print("     " + "-" * 40)

    # Step 4: Final Arena Competition
    print_banner("مرحله ۴: مسابقه نهایی در میدان نبرد (Final Competition Arena)")
    print("شرایط مسابقه:")
    print("  - نقشه کاملاً جدید و دیده نشده (Unseen Map)")
    print("  - یادگیری خاموش (Learning = OFF, Epsilon = 0)")
    print("  - رقابت همزمان بر سر منابع مشترک با ۳ رقیب هوش مصنوعی!")

    arena = MultiAgentArena(
        config=DEFAULT_CONFIG,
        grid_width=10,
        grid_height=10,
        num_coins=8,
        num_diamonds=3,
        seed=123,
    )

    # Competitor agents
    comp1 = Trainer(strategy=presets["coin_hunter"]).agent
    comp2 = Trainer(strategy=presets["cautious"]).agent
    comp3 = Trainer(strategy=presets["diamond_rusher"]).agent

    # Train competitors quickly for fair play
    Trainer(strategy=presets["coin_hunter"], agent=comp1).train(num_episodes=20)
    Trainer(strategy=presets["cautious"], agent=comp2).train(num_episodes=20)
    Trainer(strategy=presets["diamond_rusher"], agent=comp3).train(num_episodes=20)

    competitors = [
        ("player", f"عامل شما ({chosen_strat.name})", "#4CAF50", trainer.agent),
        ("comp1", "شکارچی سکه (Coin Hunter)", "#2196F3", comp1),
        ("comp2", "محتاط ترسو (Cautious Survivor)", "#FF9800", comp2),
        ("comp3", "عاشق الماس (Diamond Rusher)", "#9C27B0", comp3),
    ]

    match_result = arena.run_match(competitors, max_steps=100)

    print_banner("🏆 جدول نتایج نهایی مسابقه (Leaderboard) 🏆")
    print(f"{'رتبه':<5} | {'شرکت‌کننده':<35} | {'سکه‌های خروجی':<12} | {'جان باقی‌مانده':<14} | {'گام‌ها':<7} | {'وضعیت'}")
    print("-" * 95)
    for entry in match_result.leaderboard:
        print(f"{entry.rank:<5} | {entry.agent_name:<35} | {entry.coins_exited:<12} | {entry.lives_remaining:<14} | {entry.steps_taken:<7} | {entry.status_fa}")

    print("\nآموزش کامل با موفقیت اجرا شد!")


if __name__ == "__main__":
    main()
