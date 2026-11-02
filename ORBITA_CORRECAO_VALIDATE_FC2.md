# ORBITA_CORRECAO_VALIDATE_FC2.md

**Versão do relatório:** 0.1.0  
**Data:** 31/10/2026  
**Objetivo:** Correção do controle de entrada e saída do processo no script `validate_fc2.py`.

---

## 1. Diagnóstico Anterior

### Problema identificado
O trecho original do script:

```python
# Read output (server stays alive, so read until timeout then kill)
try:
    stdout, stderr = proc.communicate(timeout=5)
except subprocess.TimeoutExpired:
    stdout = proc.stdout.read() if proc.stdout else ""
    stderr = proc.stderr.read() if proc.stderr else ""
    proc.kill()
    proc.wait()
```

### Causa raiz
- `proc.communicate(timeout=5)` bloqueia aguardando o processo encerrar.
- O servidor MCP STDIO permanece em espera (STDIO), não sai sozinho.
- O `except TimeoutExpired` tentava usar `proc.stdout.read()` — que **bloqueia** novamente no pipe.
- O resultado era um loop de timeouts ou um processo travado.

### Arquivos afetados
- `validate_fc2.py` — script de validação MCP.

### Arquivos não afetados
- `server/src/index.mjs` — servidor MCP — **não modificado**
- `server/src/tools.mjs` — ferramentas — **não modificado**
- Dependências (`server/package.json`, `node_modules/`) — **não modificadas**
- Configurações MCP (`.mcp.json`, `mcp.json`, `plugin.json`) — **não modificadas**

---

## 2. Correção aplicada

### Código corrigido

```python
# Send all messages and read output using temp files (no blocking reads)
tmp_out = tempfile.NamedTemporaryFile(delete=False, mode='w+')
tmp_err = tempfile.NamedTemporaryFile(delete=False, mode='w+')
stdout_path = tmp_out.name
stderr_path = tmp_err.name

# Start server with stdout/stderr redirected to temp files
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

# ... (inicialização e verificação do servidor) ...

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

# Cleanup
proc.kill()
proc.wait()
os.unlink(stdout_path)
os.unlink(stderr_path)
```

### Mudanças aplicadas

| Item | Anterior | Corrigido |
|---|---|---|
| Controle de stdin | `close()` + `None` | Removido |
| Controle de saída | `read()` bloqueante | Redirecionado para arquivo temporário |
| Espera do processo | `communicate(timeout=5)` | `proc.wait(timeout=15)` |
| Encerramento | `kill()` + `wait()` | `kill()` + `wait()` + `unlink()` dos arquivos |
| Comportamento | Trava (timeout) | Execução limpa com timeout controlado |

### Princípio da correção

- **Não usar `proc.stdout.read()`** — bloqueia até que o processo feche o pipe.
- **Salvar saída em arquivo temporário** — permite ler a saída mesmo com o processo vivo.
- **Usar `proc.wait(timeout=15)`** — espera com limite, sem bloqueio infinito.
- **Usar `proc.kill()` + `proc.wait()`** — garante término do processo em caso de timeout.
- **Remover temp dir** — limpa arquivos temporários após a leitura.

---

## 3. Resultado dos testes

### Ambiente

| Item | Valor |
|---|---|
| Node.js | v26.12.1 |
| Pacote | @orbita/local-mcp-server v0.1.0 |
| Dependências | @modelcontextprotocol/server 2.4.0, zod 4.6.7 |
| Shell | git-bash / MSYS |

### Sequência de validação

| Etapa | Mensagem | Resposta | Status |
|---|---|---|---|
| Inicialização | `node src/index.mjs` | `[ORBITA] Servidor MCP iniciado. Workspace: ...` | ✅ |
| `initialize` (id=1) | `{"jsonrpc":"2.0","id":1,...}` | ✅ `{"result":{"protocolVersion":"2024-11-05",...}}` | ✅ |
| `notifications/initialized` (sem `id`) | `{"jsonrpc":"2.0","method":"notifications/initialized"}` | ✅ **sem resposta** (correto) | ✅ |
| `tools/list` (id=3) | `{"jsonrpc":"2.0","id":3,...}` | ✅ **11 ferramentas** retornadas | ✅ |
| `orbita_status` (id=4) | `{"jsonrpc":"2.0","id":4,...}` | ✅ **Status retornado** | ✅ |

### Verdict de cada teste

| Verificação | Resultado |
|---|---|
| `initialize` recebe resposta | ✅ **APROVADO** |
| `notifications/initialized` não recebe resposta | ✅ **APROVADO** |
| `tools/list` retorna 11 ferramentas | ✅ **APROVADO** |
| `orbita_status` responde corretamente | ✅ **APROVADO** |
| Processo termina sem bloqueio | ✅ **APROVADO** |
| STDOUT contém só JSON-RPC válidos | ✅ **APROVADO** |

### Distribuição do processo

| Fase | Status |
|---|---|
| Criação do processo | ✅ OK |
| Inicialização do servidor | ✅ OK |
| Envio de mensagens | ✅ OK |
| Leitura da saída | ✅ OK |
| Encerramento do processo | ✅ OK |
| Limpeza de arquivos temporários | ✅ OK |

---

## 4. Arquivos modificados

| Arquivo | Mudança | Impacto |
|---|---|---|
| `validate_fc2.py` | Controle de entrada/saída do processo MCP | **Apenas este arquivo foi modificado** |

### Arquivos NÃO modificados (confirmados)

- `server/src/index.mjs` — servidor MCP
- `server/src/tools.mjs` — 11 ferramentas
- `server/src/security.mjs`, `state.mjs`, `approvals.mjs`, `workspace.mjs`, `audit.mjs`, `process.mjs` — componentes internos
- `server/package.json` — dependências
- `server/node_modules/` — dependências instaladas
- `server/package-lock.json` — lockfile
- `server/test/` — testes
- `.mcp.json`, `mcp.json`, `plugin.json`, `.codex-plugin/plugin.json` — configurações MCP
- `README.md`, `ORBITA_ESPECIFICACAO_COMPLETA_PLUGIN_CHATGPT.md` — documentação

---

## 5. Observações finais

- A correção não alterou a lógica do protocolo MCP.
- A correção não adicionou funcionalidades novas.
- A correção não removeu funcionalidades existentes.
- A correção apenas torna o script de validação confiável, sem modificar o comportamento do servidor MCP.

---

## 6. Próximos passos

Com a validação do script determinística, a fase MCP está pronta para avançar para:

1. **Integração com o host** — testar a conexão com ChatGPT Desktop/Codex.
2. **Validação de ferramentas no host** — executar `orbita_status`, leitura de arquivos, prévias, aplicação e execução de tarefas.
3. **Preparação da distribuição privada** — montagem do pacote e verificação de instalação.

---

*Relatório gerado em 31/10/2026.*  
*Ordem técnica aplicada conforme requisitado.*  
