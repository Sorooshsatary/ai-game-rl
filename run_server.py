"""Server runner for the RL Educational Game Web UI."""

import os
import sys
import uvicorn

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))

    print("\n" + "=" * 60)
    print("  🚀 سرور وب بازی آموزشی و رقابتی RL در حال راه‌اندازی است...")
    print(f"  🌐 آدرس دسترسی در مرورگر: http://127.0.0.1:{port}")
    print("=" * 60 + "\n")

    uvicorn.run(
        "game.ui.app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
