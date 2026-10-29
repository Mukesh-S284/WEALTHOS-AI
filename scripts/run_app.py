"""Cross-platform launcher for WealthOS AI: runs FastAPI backend and Streamlit frontend concurrently."""

import sys
import os
import subprocess
import time
import signal
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
os.chdir(root_dir)


def main():
    print("=" * 60)
    print("💎 WealthOS AI — Unified Wealth Platform Launcher")
    print("=" * 60)
    print("Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    print("Starting Streamlit Frontend on http://127.0.0.1:8501 ...")
    print("Press Ctrl+C to terminate both services.")
    print("=" * 60)

    # 1. Launch FastAPI backend
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(root_dir)
    )

    # Allow backend 1.5 seconds to bind
    time.sleep(1.5)

    # 2. Launch Streamlit frontend
    frontend_proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.headless", "true"],
        cwd=str(root_dir)
    )

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print(f"Backend process terminated with code {backend_proc.returncode}")
                break
            if frontend_proc.poll() is not None:
                print(f"Frontend process terminated with code {frontend_proc.returncode}")
                break
    except KeyboardInterrupt:
        print("\nShutting down WealthOS AI services...")
    finally:
        for p in [backend_proc, frontend_proc]:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill()
        print("WealthOS AI shut down cleanly.")


if __name__ == "__main__":
    main()
