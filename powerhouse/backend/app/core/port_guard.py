"""
POWER HOUSE — Backend Port Guard & Startup Diagnostic System

Prevents duplicate backend server instances on port 8000.
Intercepts socket collisions before Winsock raises [WinError 10013].
Provides structured diagnostics on PID, process name, POWER HOUSE identity,
and /health endpoint telemetry.
"""

import os
import sys
import json
import socket
import signal
import subprocess
import urllib.request
from typing import Optional, Tuple, Dict, Any


def is_socket_busy(host: str = "127.0.0.1", port: int = 8000) -> bool:
    """Check whether a TCP connection can be established to host:port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.4)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False


def find_listening_pid(port: int = 8000) -> Optional[int]:
    """Find the PID of the process listening on the specified local port."""
    try:
        out = subprocess.check_output(
            ["netstat", "-ano", "-p", "tcp"],
            text=True,
            stderr=subprocess.DEVNULL
        )
        port_suffix = f":{port}"
        for line in out.splitlines():
            line = line.strip()
            if "LISTENING" in line:
                parts = line.split()
                if len(parts) >= 5:
                    local_addr = parts[1]
                    if local_addr.endswith(port_suffix):
                        try:
                            return int(parts[-1])
                        except ValueError:
                            pass
    except Exception:
        pass
    return None


def get_process_details(pid: int) -> Dict[str, Any]:
    """Retrieve process metadata including process name and command line."""
    details: Dict[str, Any] = {
        "pid": pid,
        "name": "Unknown",
        "command_line": "",
        "is_powerhouse": False,
    }
    if not pid:
        return details

    # 1. Query process name via tasklist
    try:
        out = subprocess.check_output(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            text=True,
            stderr=subprocess.DEVNULL
        )
        for line in out.splitlines():
            line = line.strip()
            if line and not line.startswith("INFO:"):
                # format: "python.exe","1234","Console","1","25,000 K"
                parts = [p.strip(' "') for p in line.split('","')]
                if parts:
                    details["name"] = parts[0].strip(' "')
                    break
    except Exception:
        pass

    # 2. Query command line via PowerShell CIM
    try:
        ps_cmd = f"(Get-CimInstance Win32_Process -Filter 'ProcessId = {pid}').CommandLine"
        cmd_out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            text=True,
            stderr=subprocess.DEVNULL
        )
        details["command_line"] = cmd_out.strip()
    except Exception:
        pass

    name_lower = details["name"].lower()
    cmd_lower = details["command_line"].lower()
    if "python" in name_lower or "uvicorn" in name_lower:
        if "powerhouse" in cmd_lower or "app.main" in cmd_lower or "main:app" in cmd_lower:
            details["is_powerhouse"] = True

    return details


def query_health_endpoint(host: str = "127.0.0.1", port: int = 8000, timeout: float = 1.0) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Ping http://host:port/health to verify if a healthy POWER HOUSE API is running."""
    url = f"http://{host}:{port}/health"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "POWER-HOUSE-PortGuard/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                raw = response.read().decode("utf-8")
                data = json.loads(raw)
                if data.get("status") == "healthy" and data.get("service") == "power-house-api":
                    return True, data
                return False, data
    except Exception:
        pass
    return False, None


def check_and_guard_port(host: str = "127.0.0.1", port: int = 8000) -> bool:
    """
    Pre-flight check before binding socket.
    Returns True if port is free or owned by this process.
    If occupied by another process:
      - Prints structured diagnostic telemetry matching specifications.
      - Gracefully terminates current launch attempt so WinError 10013 is prevented.
    """
    # Skip during test runs
    if "pytest" in sys.modules or os.getenv("TESTING") == "true":
        return True

    # Check if socket is actually accepting connections or in listening table
    listener_pid = find_listening_pid(port=port)
    if listener_pid is None and not is_socket_busy(host, port):
        return True

    current_pid = os.getpid()
    parent_pid = os.getppid()

    # If the listener is this process or its supervisor, proceed normally
    if listener_pid is not None and (listener_pid == current_pid or listener_pid == parent_pid):
        return True

    # Port is occupied by another process!
    proc_info = get_process_details(listener_pid) if listener_pid else {"pid": "Unknown", "name": "Unknown", "is_powerhouse": False}
    is_healthy, health_data = query_health_endpoint(host=host, port=port)

    # Format diagnostics
    print("\n" + "=" * 70, file=sys.stderr)
    print(f"PORT {port} IS ALREADY IN USE", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"PID:             {listener_pid if listener_pid else 'Occupied'}", file=sys.stderr)
    print(f"Process Name:    {proc_info['name']}", file=sys.stderr)

    if is_healthy:
        print("Is POWER HOUSE:  YES (power-house-api)", file=sys.stderr)
        print("Health Status:   HEALTHY (200 OK)", file=sys.stderr)
        print(f"Health Response: {json.dumps(health_data)}", file=sys.stderr)
        print(f"Health URL:      http://{host}:{port}/health", file=sys.stderr)
        print("-" * 70, file=sys.stderr)
        print("DIAGNOSTIC STATUS:", file=sys.stderr)
        print(f"  A healthy POWER HOUSE backend is already active on http://{host}:{port}.", file=sys.stderr)
        print(f"  To prevent duplicate backend instances and socket collisions [WinError 10013],", file=sys.stderr)
        print("  this second Uvicorn instance will NOT be started.", file=sys.stderr)
        print("", file=sys.stderr)
        print("RECOMMENDED ACTIONS:", file=sys.stderr)
        print(f"  * Reuse the running backend: http://{host}:{port}", file=sys.stderr)
        print(f"  * View interactive API Docs: http://{host}:{port}/docs", file=sys.stderr)
        if listener_pid:
            print(f"  * To force restart, stop PID {listener_pid} first:", file=sys.stderr)
            print(f"    powershell: Stop-Process -Id {listener_pid}", file=sys.stderr)
    elif proc_info.get("is_powerhouse"):
        print("Is POWER HOUSE:  YES (Stale / Unresponsive process)", file=sys.stderr)
        print("Health Status:   UNRESPONSIVE (No response from /health)", file=sys.stderr)
        print(f"Health URL:      http://{host}:{port}/health", file=sys.stderr)
        print("-" * 70, file=sys.stderr)
        print("DIAGNOSTIC STATUS:", file=sys.stderr)
        print(f"  Port {port} is occupied by a stale POWER HOUSE process (PID: {listener_pid}).", file=sys.stderr)
        print("  The process is holding the port but the health endpoint is not responding.", file=sys.stderr)
        print("", file=sys.stderr)
        print("RECOMMENDED ACTIONS:", file=sys.stderr)
        if listener_pid:
            print(f"  * Stop the stale process safely:", file=sys.stderr)
            print(f"    powershell: Stop-Process -Id {listener_pid}", file=sys.stderr)
        print("  * Or run .\\run.ps1 which recycles stale POWER HOUSE processes automatically.", file=sys.stderr)
    else:
        print("Is POWER HOUSE:  NO (Unrelated external process)", file=sys.stderr)
        print("Health Status:   NO RESPONSE from POWER HOUSE /health", file=sys.stderr)
        print(f"Health URL:      http://{host}:{port}/health", file=sys.stderr)
        print("-" * 70, file=sys.stderr)
        print("DIAGNOSTIC STATUS:", file=sys.stderr)
        print(f"  Port {port} is occupied by an external application ({proc_info['name']}).", file=sys.stderr)
        print(f"  Uvicorn cannot bind to {host}:{port}.", file=sys.stderr)
        print("", file=sys.stderr)
        print("RECOMMENDED ACTIONS:", file=sys.stderr)
        print(f"  * Close the conflicting application or stop PID {listener_pid} manually.", file=sys.stderr)
        print("  * Automatic kill was omitted to protect unrelated applications.", file=sys.stderr)

    print("=" * 70 + "\n", file=sys.stderr)

    # Terminate the uvicorn supervisor process if running with --reload
    if parent_pid and parent_pid != os.getpid():
        try:
            parent_details = get_process_details(parent_pid)
            parent_name = parent_details["name"].lower()
            if "python" in parent_name or "uvicorn" in parent_name:
                os.kill(parent_pid, signal.SIGTERM)
        except Exception:
            pass

    # Exit cleanly without letting Uvicorn raise WinError 10013
    sys.exit(0)
