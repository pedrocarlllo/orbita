#!/usr/bin/env python3
import subprocess
import json
import sys
import time
import os
import tempfile

SERVER_DIR = "C:/ORBITA-Universal-Plugin-Windows-0.1.0/orbita-agent/server"

print("=== ORBITA CORREÇÃO VALIDATE_FC2 ===")

# Create temp files for stdout and stderr
tmp_out = tempfile.NamedTemporaryFile(delete=False, mode='w+')
tmp_err = tempfile.NamedTemporaryFile(delete=False, mode='w+')
stdout_path = tmp_out.name
stderr_path = tmp_err.name

# Start server with stdout/stderr redirected to files
proc = subprocess.Popen(
    ["node", "src/index.mjs"],
    cwd=SERVER_DIR,
    stdin=subprocess.PIPE,
    stdout=open(stdout_path, 'w'),
    stderr=open(stderr_path, 'w'),
    text=True,
    env=dict(os.environ)
)

time.sleep(2.5)

# Read initial output from files
with open(stdout_path, 'r') as f:
    stdout_init = f.read().strip()
with open(stderr_path, 'r') as f:
    stderr_init = f.read().strip()

print(f"Initial stdout: {stdout_init}")
print(f"Initial stderr: {stderr_init}")

if proc.poll() is not None:
    print(f"Server died: {proc.returncode}")
    sys.exit(1)

print(f"Server UP (PID={proc.pid})")

# Messages
msgs = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}
    },
    {"jsonrpc": "2.0", "method": "notifications/initialized"},  # NO ID - correct notification
    {"jsonrpc": "2.0", "id": 3, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "orbita_status"}},
]

input_str = "".join(json.dumps(m) + "\n" for m in msgs)

# Send all messages and close stdin
proc.stdin.write(input_str)
proc.stdin.flush()
proc.stdin.close()

# Wait for process to exit with timeout
try:
    proc.wait(timeout=15)
except subprocess.TimeoutExpired:
    proc.kill()
    proc.wait()

# Read output from files
with open(stdout_path, 'r') as f:
    stdout = f.read()
with open(stderr_path, 'r') as f:
    stderr = f.read()

print("\n=== RESPOSTAS ===")
for line in stdout.split("\n"):
    print(f"  {line.strip()}")

print("\n=== RESTANTE STDOUT ===")
print(stdout)
print("=== RESTANTE STDERR ===")
print(stderr)

# Check for Method not found
if '"Method not found"' in stderr or '"Method not found"' in stdout:
    print("\n[WARN] Método 'not found' ainda presente")
else:
    print("\n[OK] Nenhum 'Method not found'")

# Check tools response
if '"tools"' in stdout and '"result"' in stdout:
    print("\n[OK] tools/list retornou ferramentas")
else:
    print("\n[FAIL] tools/list não retornou ferramentas")

# Check status response - need to handle escaped quotes in JSON
status_text = stdout.replace('\\"name\\"', '"name"')
if '"name":"ORBITA"' in status_text or '"name": "ORBITA"' in status_text.replace('\\"','"'):
    print("\n[OK] orbita_status retornou status")
else:
    print("\n[FAIL] orbita_status não retornou status")

# Cleanup
proc.kill()
proc.wait()
os.unlink(stdout_path)
os.unlink(stderr_path)
print("\n[OK] Processo encerrado sem bloqueio")
