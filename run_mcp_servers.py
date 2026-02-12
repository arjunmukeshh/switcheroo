import subprocess
import sys
import os
import time
import signal

# List of servers to run
# Format: (name, script_path, port)
SERVERS = [
    ("Wiz Bulb Server", "mcp_servers/wiz_bulb/wiz_server.py", 8001),
    ("Timekeeper Agent", "mcp_servers/timekeeper/timekeeper.py", 8002),
    ("Telegram Agent", "mcp_servers/telegram/telegram_bot.py", 8003),
    ("Servo Controller", "mcp_servers/servo/servo_mcp.py", 8004),
    ("Telegram Gateway", "mcp_servers/telegram/telegram_gateway.py", None)
]

processes = []

def signal_handler(sig, frame):
    print("\nShutting down all MCP servers...")
    for p, name in processes:
        print(f"Stopping {name}...")
        p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def run_servers():
    print("Starting all MCP servers in streamable-http mode...\n")
    
    for name, path, port in SERVERS:
        if not os.path.exists(path):
            print(f"Warning: {path} not found. Skipping {name}.")
            continue
            
        print(f"Launching {name} on port {port}...")
        
        # Use sys.executable to ensure we use the same python environment
        cmd = [sys.executable, path]
        
        if port:
            cmd.extend(["--transport", "streamable-http", "--port", str(port)])
        
        process = subprocess.Popen(cmd)
        processes.append((process, name))
        
    print("\nAll servers launched. Press Ctrl+C to stop all.")
    
    # Keep the script running
    while True:
        time.sleep(1)

if __name__ == "__main__":
    run_servers()
