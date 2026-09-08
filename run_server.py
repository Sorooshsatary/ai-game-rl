"""Server runner for the RL Educational Game Web UI."""

import sys
import uvicorn

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def main():
    print("\n" + "=" * 60)
    print("  🚀 سرور وب بازی آموزشی و رقابتی RL در حال راه‌اندازی است...")
    print("  🌐 آدرس دسترسی در مرورگر: http://127.0.0.1:8000")
    print("=" * 60 + "\n")

    uvicorn.run(
        "game.ui.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
