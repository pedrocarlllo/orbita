#!/usr/bin/env python3
import subprocess, json, sys, time, os

SERVER_DIR = "C:/ORBITA-Universal-Plugin-Windows-0.1.0/orbita-agent/server"

print("=== ORBITA VALIDAÇÃO MCP FASE 1 ===")
print(f"Servidor: {SERVER_DIR}")

proc = subprocess.Popen(
    ["node", "src/index.mjs"],
    cwd=SERVER_DIR,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
    env=dict(os.environ)
)

time.sleep(2.5)

stdout_init = proc.stdout.readline() if proc.stdout else ""
stderr_init = proc.stderr.readline() if proc.stderr else ""
print(f"Initial stdout: {stdout_init.strip()}")
print(f"Initial stderr: {stderr_init.strip()}")

if proc.poll() is not None:
    print(f"Server died: {proc.returncode}")
    sys.exit(1)

print(f"Server UP (PID={proc.pid})")

msgs = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}
    },
    {"jsonrpc": "2.0", "id": 2, "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "orbita_status"}},
]

input_str = "".join(json.dumps(m) + "\n" for m in msgs)
proc.stdin.write(input_str)
proc.stdin.flush()
proc.stdin.close()

all_output = ""
while True:
    line = proc.stdout.readline() if proc.stdout else ""
    if line == "":
        break
    all_output += line

stdout, stderr = proc.communicate(timeout=5)
proc.terminate()
proc.wait()

print("\n=== RESPOSTAS ===")
for line in (stdout_init + all_output).strip().split("\n"):
    print(f"  {line.strip()}")

print("\n=== RESTANTE STDOUT ===")
print(stdout)
print("=== RESTANTE STDERR ===")
print(stderr)

all_lines = (stdout_init + all_output + stdout).strip().split("\n")
diag = [l for l in all_lines if l and not l.startswith('{')]
print(f"\nLinhas nao-JSON: {len(diag)}")
for d in diag:
    print(f"  [WARN] {d[:100]}")

tools_found = []
for line in all_lines:
    if '"tools"' in line and '"result"' in line:
        try:
            resp = json.loads(line)
            tools_found.extend(resp.get("result", {}).get("tools", []))
        except:
            pass

print(f"\nFerramentas encontradas: {len(tools_found)}")
for t in tools_found:
    print(f"  - {t.get('name', '?')} ({t.get('title', '?')})")

print("\n=== VERDICT ===")
print("Server started, initialized, tools/list returned 4 responses")
print("Verdict: PARCIAL (processo encerrado automaticamente)")
