"""
LandSense - One-command launcher
Run from the project root:  python scripts/run_all.py

What it does
------------
1. Frees any ports already in use (kills the owning process first).
2. Starts every service as a proper Python module so imports always resolve.
3. Waits for each service to pass a health-check before moving on.
4. Tails all service logs to a single combined terminal stream with colour tags.
5. Ctrl+C cleanly stops everything.
"""

import os
import sys
import time
import signal
import socket
import subprocess
import threading
import webbrowser
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

ARM64_PYTHON = r"C:\Landsense\true_snapdragon_env\Scripts\python.exe"
AI_PYTHON = ARM64_PYTHON if os.path.exists(ARM64_PYTHON) else sys.executable

SERVICES = [
    # name            module / command (list)                              port   health-url                       required
    ("AI Service",    [AI_PYTHON, "-m", "ai.main"],                        8001,  "http://localhost:8001/health",  True),
    ("IoT Service",   [sys.executable, "-m", "uvicorn",
                       "iot.main:app", "--host", "0.0.0.0",
                       "--port", "8002",
                       "--reload", "--reload-dir", "iot"],                 8002,  "http://localhost:8002/sensor",  False),
    ("Cloud Service", [sys.executable, "-m", "cloud.main"],                8003,  "http://localhost:8003/heatmap", False),
    ("MCP Service",   [sys.executable, "-m", "uvicorn",
                       "mcp.main:app", "--host", "0.0.0.0",
                       "--port", "8004",
                       "--reload", "--reload-dir", "mcp"],                 8004,  "http://localhost:8004/status",  False),
    ("Backend",       [sys.executable, "-m", "backend.main"],              8000,  "http://localhost:8000/health",  True),
    ("Web Dashboard", [sys.executable, "-m", "http.server", "8080",
                       "--directory", "web"],                              8080,  None,                            False),
]

HEALTH_TIMEOUT   = 30   # seconds to wait for a service to become healthy
HEALTH_INTERVAL  = 0.5  # seconds between retries
LOG_PREFIX_WIDTH = 14   # chars to pad service name column

# ANSI colours (Windows 10+ supports these natively)
COLOURS = {
    "AI Service":    "\033[95m",   # magenta
    "IoT Service":   "\033[96m",   # cyan
    "Cloud Service": "\033[94m",   # blue
    "MCP Service":   "\033[93m",   # yellow
    "Backend":       "\033[92m",   # green
    "Web Dashboard": "\033[90m",   # dark grey
    "LAUNCHER":      "\033[97m",   # white
}
RESET  = "\033[0m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def tag(name: str) -> str:
    colour = COLOURS.get(name, "")
    return f"{colour}[{name:<{LOG_PREFIX_WIDTH}}]{RESET}"


def log(name: str, msg: str) -> None:
    print(f"{tag(name)} {msg}", flush=True)


def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def free_port(port: int) -> None:
    """Kill whatever is holding the port (Windows-compatible)."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 5 and f":{port}" in parts[1] and parts[3] == "LISTENING":
                owning_pid = int(parts[4])
                subprocess.run(
                    ["taskkill", "/PID", str(owning_pid), "/F"],
                    capture_output=True, timeout=5
                )
                log("LAUNCHER", f"{YELLOW}Freed port {port} (killed PID {owning_pid}){RESET}")
                time.sleep(0.5)
                return
    except Exception as exc:
        log("LAUNCHER", f"{RED}Could not free port {port}: {exc}{RESET}")


def wait_healthy(name: str, url: str | None, timeout: float) -> bool:
    """Poll url until 200 or timeout. Returns True if healthy."""
    if url is None:
        time.sleep(1)
        return True

    # lazy-import so the script itself has no deps beyond stdlib
    try:
        import urllib.request
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=2) as r:
                    if r.status == 200:
                        return True
            except Exception:
                pass
            time.sleep(HEALTH_INTERVAL)
        return False
    except ImportError:
        time.sleep(2)
        return True


def stream_output(proc: subprocess.Popen, name: str) -> None:
    """Background thread: forward a process's stdout+stderr to our terminal."""
    try:
        for raw in proc.stdout:  # type: ignore[union-attr]
            line = raw.rstrip("\n").rstrip("\r\n") if isinstance(raw, str) else raw.rstrip(b"\n").rstrip(b"\r\n").decode("utf-8", errors="replace")
            print(f"{tag(name)} {line}", flush=True)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

processes: list[subprocess.Popen] = []


def cleanup(sig=None, frame=None) -> None:
    print(f"\n{tag('LAUNCHER')} {YELLOW}Stopping all services...{RESET}", flush=True)
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    for p in processes:
        try:
            p.wait(timeout=3)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    print(f"{tag('LAUNCHER')} {GREEN}All services stopped. Goodbye.{RESET}", flush=True)
    sys.exit(0)


def main() -> None:
    if sys.platform == "win32":
        import msvcrt
        lock_file = ROOT / ".run_all.lock"
        try:
            # We open the lock file and keep the fd open for the lifetime of the process.
            # We must use global or attach it to an object so the fd isn't garbage collected and closed.
            global _lock_fd
            _lock_fd = os.open(lock_file, os.O_CREAT | os.O_TRUNC | os.O_RDWR)
            msvcrt.locking(_lock_fd, msvcrt.LK_NBLCK, 1)
        except OSError:
            print(f"{RED}ERROR: Another instance of run_all.py is already running. Please close it first.{RESET}")
            sys.exit(1)

    # Enable ANSI on Windows
    os.system("color")

    signal.signal(signal.SIGINT,  cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    print(f"""
{COLOURS['LAUNCHER']}+======================================================+
|         LandSense  -  Single-command Launcher        |
+======================================================+{RESET}
""", flush=True)

    for name, cmd, port, health_url, required in SERVICES:

        # 1. Free port if occupied
        if port_in_use(port):
            log("LAUNCHER", f"{YELLOW}Port {port} already in use — freeing it...{RESET}")
            free_port(port)
            time.sleep(0.5)

        # 2. Start process
        log("LAUNCHER", f"Starting {name} on port {port}...")
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(ROOT),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except Exception as exc:
            log(name, f"{RED}FAILED to start: {exc}{RESET}")
            if required:
                log("LAUNCHER", f"{RED}Required service '{name}' could not start. Aborting.{RESET}")
                cleanup()
            continue

        processes.append(proc)

        # 3. Stream its output in background
        t = threading.Thread(target=stream_output, args=(proc, name), daemon=True)
        t.start()

        # 4. Wait until healthy
        if health_url:
            log("LAUNCHER", f"Waiting for {name} to be healthy (up to {HEALTH_TIMEOUT}s)...")
            ok = wait_healthy(name, health_url, HEALTH_TIMEOUT)
            if ok:
                log("LAUNCHER", f"{GREEN}{name} is UP  ({health_url}){RESET}")
            else:
                log("LAUNCHER", f"{RED}{name} did NOT become healthy in {HEALTH_TIMEOUT}s.{RESET}")
                if required:
                    log("LAUNCHER", f"{RED}Required service failed. Shutting down.{RESET}")
                    cleanup()
        else:
            time.sleep(1)
            log("LAUNCHER", f"{GREEN}{name} started (no health-check endpoint).{RESET}")

    # All services launched
    print(f"""
{GREEN}+======================================================+
|           All systems are running!                   |
+------------------------------------------------------+
|  Backend API    ->  http://localhost:8000             |
|  AI Service     ->  http://localhost:8001             |
|  IoT Service    ->  http://localhost:8002             |
|  Cloud Service  ->  http://localhost:8003             |
|  MCP Service    ->  http://localhost:8004             |
|  Web Dashboard  ->  http://localhost:8080             |
+======================================================+{RESET}
""", flush=True)

    time.sleep(1)
    webbrowser.open("http://localhost:8080")

    log("LAUNCHER", "Press Ctrl+C to stop all services.")

    MAX_RESTARTS = 3
    RESTART_DELAY = 3   # seconds before restarting
    restart_counts: dict[str, int] = {name: 0 for name, *_ in SERVICES}

    # Keep alive, auto-restart crashed services
    while True:
        time.sleep(2)
        for i, (name, cmd, port, health_url, required) in enumerate(SERVICES):
            if i >= len(processes):
                break
            proc = processes[i]
            if proc.poll() is None:
                continue  # still running

            exit_code = proc.returncode
            restart_counts[name] += 1
            attempt = restart_counts[name]

            if attempt > MAX_RESTARTS:
                log(name, f"{RED}Crashed (code {exit_code}) and exceeded {MAX_RESTARTS} restart attempts — giving up.{RESET}")
                if required:
                    log("LAUNCHER", f"{RED}Required service '{name}' permanently down. Shutting down.{RESET}")
                    cleanup()
                continue

            log(name, f"{YELLOW}Crashed (code {exit_code}). Restart {attempt}/{MAX_RESTARTS} in {RESTART_DELAY}s...{RESET}")
            time.sleep(RESTART_DELAY)

            # Free the port in case it's still TIME_WAIT
            if port_in_use(port):
                free_port(port)

            try:
                new_proc = subprocess.Popen(
                    cmd,
                    cwd=str(ROOT),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                processes[i] = new_proc
                threading.Thread(target=stream_output, args=(new_proc, name), daemon=True).start()
                log(name, f"{YELLOW}Restarted (PID {new_proc.pid}). Waiting for health...{RESET}")
                ok = wait_healthy(name, health_url, HEALTH_TIMEOUT)
                if ok:
                    log(name, f"{GREEN}Back up after restart {attempt}.{RESET}")
                    restart_counts[name] = 0  # reset counter on successful recovery
                else:
                    log(name, f"{RED}Did not recover after restart {attempt}.{RESET}")
            except Exception as exc:
                log(name, f"{RED}Failed to restart: {exc}{RESET}")


if __name__ == "__main__":
    main()
