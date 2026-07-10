import subprocess
import time
import sys
import os
import webbrowser
import signal

processes = []

def cleanup():
    print("\nTerminating all services...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=2)
        except Exception:
            pass
    print("Services shutdown complete.")

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

def main():
    # Set PYTHONPATH to include the project root so imports work
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root

    print("===================================================================")
    print("           LandSense AI Multi-Device Simulator Bootstrapper        ")
    print("===================================================================")

    # Register cleanup handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # 1. Start AI service (Port 8001)
        print("Starting AI Service on port 8001...")
        p_ai = subprocess.Popen(
            [sys.executable, "ai/main.py"],
            cwd=project_root,
            env=env
        )
        processes.append(p_ai)

        # 2. Start IoT sensor service (Port 8002)
        print("Starting IoT Service on port 8002...")
        p_iot = subprocess.Popen(
            [sys.executable, "iot/main.py"],
            cwd=project_root,
            env=env
        )
        processes.append(p_iot)

        # 3. Start Cloud Sync service (Port 8003)
        print("Starting Qualcomm Cloud Service on port 8003...")
        p_cloud = subprocess.Popen(
            [sys.executable, "-m", "cloud.main"],
            cwd=project_root,
            env=env
        )
        processes.append(p_cloud)

        # 4. Start MCP registry service (Port 8004)
        print("Starting MCP Service on port 8004...")
        p_mcp = subprocess.Popen(
            [sys.executable, "mcp/main.py"],
            cwd=project_root,
            env=env
        )
        processes.append(p_mcp)

        # Allow dummy services to bind to ports
        time.sleep(2)

        # 5. Start Backend main orchestrator (Port 8000)
        print("Starting Backend Orchestrator on port 8000...")
        p_backend = subprocess.Popen(
            [sys.executable, "-m", "backend.main"],
            cwd=project_root,
            env=env
        )
        processes.append(p_backend)

        # 6. Start Web server to serve static frontend dashboard (Port 8080)
        print("Starting Local Web Server on port 8080...")
        p_web = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8080", "--directory", "web"],
            cwd=project_root,
            env=env
        )
        processes.append(p_web)

        time.sleep(2)
        print("\nAll systems successfully initialized.")
        print("- Backend: http://localhost:8000")
        print("- Web Dashboard: http://localhost:8080")
        print("\nOpening web browser dashboard...")
        webbrowser.open("http://localhost:8080")

        print("\nPress Ctrl+C to terminate all services.")
        
        # Keep main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        print(f"Startup error: {str(e)}")
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
