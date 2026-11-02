#!/usr/bin/env python3
"""Validação Fase 1: MCP STDIO do ORBITA."""
import subprocess
import json
import sys
import time
import os

SERVER_DIR = "/c/ORBITA-Universal-Plugin-Windows-0.1.0/orbita-agent/server"
RESULTS = []

def log_test(test_name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    RESULTS.append({"test": test_name, "status": status, "detail": detail})
    print(f"  [{status}] {test_name}")
    if detail:
        for line in detail.split("\n"):
            print(f"      {line}")

def send_json(rpc_id, method, params=None):
    """Envia uma mensagem JSON-RPC via stdin do processo."""
    msg = {"jsonrpc": "2.0", "id": rpc_id}
    if method:
        msg["method"] = method
    if params:
        msg["params"] = params
    return msg

# ===== TESTE 1: INICIALIZAÇÃO =====
print("=== TESTE 1: INICIALIZAÇÃO STDIO ===")
proc = subprocess.Popen(
    ["node", "src/index.mjs"],
    cwd=SERVER_DIR,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)
time.sleep(2.0)

stdout_initial = proc.stdout.readline() if proc.stdout else ""
stderr_initial = proc.stderr.readline() if proc.stderr else ""
print(f"  stdout: {stdout_initial.strip()}")
print(f"  stderr: {stderr_initial.strip()}")

if proc.poll() is not None:
    log_test("Inicialização", False, f"processo terminou: exit={proc.returncode}")
    proc.kill()
    sys.exit(1)
else:
    log_test("Inicialização", True, f"PID={proc.pid}")

# ===== TESTE 2: INITIALIZE =====
print("=== TESTE 2: REQUEST initialize ===")
init_msg = send_json(1, "initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "test-client", "version": "1.0.0"}
})
proc.stdin.write(json.dumps(init_msg) + "\n")
proc.stdin.flush()

init_response = proc.stdout.readline() if proc.stdout else ""
print(f"  resposta: {init_response.strip()}")
try:
    resp = json.loads(init_response)
    if resp.get("jsonrpc") == "2.0" and resp.get("id") == 1:
        log_test("initialize", True, f"version={resp.get('result', {}).get('protocolVersion', 'N/A')}")
    else:
        log_test("initialize", False, f"resposta inválida: {init_response}")
except json.JSONDecodeError:
    log_test("initialize", False, f"não é JSON: {init_response}")

# ===== TESTE 3: NOTIFICATIONS/INITIALIZED =====
print("=== TESTE 3: NOTIFICATIONS/INITIALIZED ===")
proc.stdin.write(json.dumps(send_json(2, "notifications/initialized")) + "\n")
proc.stdin.flush()
time.sleep(0.3)
resp = proc.stdout.readline() if proc.stdout else ""
if resp.strip() == "":
    log_test("notifications/initialized", True, "sem saída (ok, promessa nula)")
else:
    log_test("notifications/initialized", False, f"resposta inesperada: {resp.strip()}")

# ===== TESTE 4: TOOLS/LIST =====
print("=== TESTE 4: REQUEST tools/list ===")
proc.stdin.write(json.dumps(send_json(3, "tools/list")) + "\n")
proc.stdin.flush()

tools_response = proc.stdout.readline() if proc.stdout else ""
print(f"  resposta: {tools_response.strip()}")
try:
    tools_resp = json.loads(tools_response)
    tools = tools_resp.get("result", {}).get("tools", [])
    log_test("tools/list", True, f"total={len(tools)}")
except json.JSONDecodeError:
    log_test("tools/list", False, f"resposta inválida: {tools_response}")

# ===== TESTE 5: VERIFICAR 11 FERRAMENTAS =====
print("=== TESTE 5: VERIFICAR 11 FERRAMENTAS ===")
tools = tools_resp.get("result", {}).get("tools", [])
expected = [
    "orbita_status", "orbita_set_workspace_root", "orbita_list_files",
    "orbita_read_file", "orbita_search_files", "orbita_inspect_project",
    "orbita_git_status", "orbita_git_diff", "orbita_prepare_file_change",
    "orbita_apply_file_change", "orbita_run_project_task"
]
if len(tools) == 11:
    names = [t.get("name", "") for t in tools]
    if all(name in names for name in expected):
        log_test("11 ferramentas", True, f"quantidade={len(tools)}")
    else:
        log_test("11 ferramentas", False, f"faltando: {set(expected) - set(names)}")
else:
    log_test("11 ferramentas", False, f"quantidade={len(tools)}")

# ===== TESTE 6: REGISTRAR ESCANOS DAS FERRAMENTAS =====
print("=== TESTE 6: REGISTRAR ESCANOS ===")
for tool in tools:
    print(f"  {tool.get('name', '?')}")
    print(f"    title: {tool.get('title', '?')}")
    print(f"    description: {tool.get('description', '?')}")
    print(f"    inputSchema: {json.dumps(tool.get('inputSchema', {}), ensure_ascii=False)}")
    print(f"    annotations: {json.dumps(tool.get('annotations', {}), ensure_ascii=False)}")

# ===== TESTE 7: ORBITA_STATUS =====
print("=== TESTE 7: ORBITA_STATUS ===")
proc.stdin.write(json.dumps(send_json(4, "tools/call", {"name": "orbita_status"})) + "\n")
proc.stdin.flush()

status_response = proc.stdout.readline() if proc.stdout else ""
print(f"  resposta: {status_response.strip()}")
try:
    status_resp = json.loads(status_response)
    result = status_resp.get("result", {})
    if "error" in status_resp:
        log_test("orbita_status", False, f"erro: {status_resp['error']}")
    else:
        log_test("orbita_status", True, f"name={result.get('name')}, version={result.get('version')}, workspace={result.get('workspaceRoot', 'N/A')}")
except json.JSONDecodeError:
    log_test("orbita_status", False, f"resposta inválida: {status_response}")

# ===== TESTE 8: STDOUT LIMPO =====
print("=== TESTE 8: STDOUT RESERVADO AO PROTOCOLO ===")
# Read up to 5 lines and check for non-JSON diagnostics
diagnostic_lines = 0
for _ in range(3):
    line = proc.stdout.readline() if proc.stdout else ""
    if line == "":
        break
    if line.strip() and not line.strip().startswith("{"):
        diagnostic_lines += 1
        print(f"  [WARN] linhas nao-JSON: {line.strip()}")
if diagnostic_lines == 0:
    log_test("stdout limpo", True, "todas as linhas são JSON-RPC")
else:
    log_test("stdout limpo", False, f"{diagnostic_lines} linhas nao-JSON")

# ===== RESUMO =====
print("\n=== RESUMO ===")
passed = sum(1 for r in RESULTS if r["status"] == "PASS")
total = len(RESULTS)
for r in RESULTS:
    print(f"  [{r['status']}] {r['test']}")

if passed == total:
    verdict = "APROVADO"
elif passed == 0:
    verdict = "REPROVADO"
else:
    verdict = "PARCIAL"
print(f"\nVerdict: {verdict} ({passed}/{total} testes passaram)")

# Cleanup
proc.stdin.close()
proc.terminate()
try:
    proc.wait(timeout=3)
except subprocess.TimeoutExpired:
    proc.kill()

# Write report
report_path = "/c/ORBITA-Universal-Plugin-Windows-0.1.0/orbita-agent/ORBITA_VALIDACAO_MCP_FASE1.md"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(f"# ORBITA_VALIDACAO_MCP_FASE1.md\n\n")
    f.write(f"**Versão da validação:** 0.1.0\n")
    f.write(f"**Data:** 31/10/2026\n\n")
    f.write(f"## Resultado Final\n\n")
    f.write(f"Verdict: **{verdict}** ({passed}/{total} testes passaram)\n\n")
    f.write(f"## Testes Detalhados\n\n")
    for r in RESULTS:
        f.write(f"### {r['test']}: {r['status']}\n\n")
        f.write(f"{r['detail']}\n\n")

    f.write(f"## Ferramentas MCP Encontradas\n\n")
    f.write(f"| Nome | Title | Annotations |\n")
    f.write(f"|------|-------|-------------|\n")
    for tool in tools:
        f.write(f"| `{tool.get('name', '')}` | {tool.get('title', '')} | {json.dumps(tool.get('annotations', {}), ensure_ascii=False)} |\n")

    f.write(f"\n## Comandos Executados\n\n")
    f.write(f"1. `cd server && node src/index.mjs` (STDIO)\n")
    f.write(f"2. `initialize` (id=1)\n")
    f.write(f"3. `notifications/initialized` (id=2)\n")
    f.write(f"4. `tools/list` (id=3)\n")
    f.write(f"5. `tools/call orbita_status` (id=4)\n\n")

    f.write(f"## Saídas MCP\n\n")
    for r in RESULTS:
        f.write(f"- {r['test']}: {r['status']} - {r['detail']}\n")
    f.write(f"\n## Veredito\n\n")
    f.write(f"**{verdict}** - Validação do servidor MCP STDIO concluída.\n")
    f.write(f"\n**Observação:** Esta fase valida apenas o servidor e o protocolo MCP.\n")

print(f"\nRelatório salvo em: {report_path}")
