# ORBITA_DIAGRAMA_ARQUITETURAL.md

**Versão do documento:** 1.0
**Data:** 31/10/2026
**Projeto:** ORBITA Universal Windows Server

---

## 1. VISÃO GERAL

Este documento apresenta os diagramas de componentes e fluxo de dados da ORBITA em dois modos:

- **MODO A — MCP STDIO:** cliente (ChatGPT Desktop / Codex) → servidor MCP STDIO
- **MODO B — Serviço Windows:** cliente remoto → serviço Windows (Streamable HTTP)

### 1.1 Layout de componentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CLIENTES / HOSTS                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ ChatGPT      │  │ Codex        │  │ Web dashboard│  │ Outros hosts     │ │
│  │ Desktop      │  │ (CLI)        │  │ (Streamable) │  │ MCP (STDIO)      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌──────────────────────────┐  ┌──────────────┐  ┌──────────────┐
│  MODO A — MCP STDIO      │  │  MODO B —     │  │  MODO C —    │
│  (local, ambientes       │  │  Serviço      │  │  Modo유예     │
│   desktop)               │  │  Windows     │  │  (futuro)    │
└──────────────────────────┘  └──────────────┘  └──────────────┘
        │                            │                │
        ▼                            ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ORBITA NÚCLEO COMPARTILHADO                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Registro de  │  │ Gestão de    │  │ Sistema de   │  │ Aprovações   │    │
│  │ ferramentas  │  │ workspace    │  │ segurança    │  │ (tokens de   │    │
│  │ (tools.mjs)  │  │ (state.mjs)  │  │ (security.mjs)│  │ prévia)      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                       │
│  │ Auditoria    │  │ Controle de  │  │ Configuração│                       │
│  │ (audit.mjs)  │  │ processos    │  │ (state.mjs)  │                       │
│  └──────────────┘  └──────────────┘  └──────────────┘                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                       │
│  │ Transportes  │  │ Tiago        │  │ Transportes  │                       │
│  │ STDIO        │  │ (process.mjs)│  │ Streamable-  │                       │
│  │ (stdio.mjs)  │  │              │  │ HTTP         │                       │
│  └──────────────┘  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. MODO A — MCP STDIO

### 2.1 Fluxo de comunicação

```
ChatGPT Desktop / Codex (Host)
   │
   │ 1. Ler .mcp.json
   ▼
   │ 2. Lançar: node server/src/index.mjs (cwd = server/)
   ▼
   │ 3. Inicialização: initialize (id=1)
   ▼
   │ 4. Notificação: notifications/initialized (sem id)
   ▼
   │ 5. Descoberta: tools/list → 11 ferramentas
   ▼
   │ 6. tools/call → execução
   ▼
   ORBITA MCP SERVER (Node.js)
   │   • McpServer
   │   • registerTool
   │   • serveStdio
   │
   ▼
   │ 7. Response JSON-RPC
   ▼
ChatGPT Desktop / Codex
```

### 2.2 Componentes do modo A

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CLIENTE (ChatGPT Desktop / Codex)                                         │
│  • Lê .mcp.json                                                          │
│  • Inicia processo node server/src/index.mjs (cwd = server/)              │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ORBITA MCP SERVER (Node.js)                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │ McpServer    │  │ tools/mjs    │  │ serveStdio   │                      │
│  │ (SDK 2.4.0)  │  │ (dados)      │  │ (STDIO)      │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │ tools.mjs    │  │ tools.mjs    │  │ tools.mjs    │                      │
│  │ (registro)   │  │ (handler)    │  │ (handlers)   │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ENTIDADES NÚCLEO                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │ state.mjs    │  │ security.mjs │  │ audit.mjs    │                      │
│  │ (workspace)  │  │ (guards)     │  │ (JSONL)      │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │ approvals.mjs│  │ process.mjs  │  │ registry.mjs │                      │
│  │ (tokens)     │  │ (execução)   │  │ (tools map)  │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ARQUIVOS                                                                │
│  • workspaceRoot (pasta ativa do usuário)                                 │
│  • config.json (pasta de dados)                                          │
│  • audit.jsonl (registro de ações)                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Vetor de fluxo de dados

```
Entrada do cliente                          Saída do núcleo
───────────────────                         ──────────────
initialize (id=1) ──► HTTP/JSON-RPC response
notifications/initialized ──► (não há resp) ← count tools
tools/list ─────────► tools[] (11 nomes)
tools/call ─────────► response { content: [{ type: "text", text }] }
orch_status ─────────► response { name, version, ... }
```

---

## 3. MODO B — Serviço Windows

### 3.1 Arquitetura do serviço

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CLIENTE REMOTO (ChatGPI/Codex/Outro)                                      │
│  • Autentica (Bearer token / certificado)                                   │
│  • Envia JSON-RPC via POST /mcp                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SERVIÇO WINDOWS (ORBITA)                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  HTTP Server (Node.js http/https)                                   │   │
│  │  • GET  /health (health check)                                      │   │
│  │  • POST /mcp (Streamable HTTP — JSON-RPC)                          │   │
│  │  • GET  /mcp (log)                                                │   │
│  │  • POST /auth (autenticação)                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Autenticação / Autorização                                         │   │
│  │  • Bearer token / certificado                                       │   │
│  │  • Políticas de aprovação (readOnly, destructive, openWorld)       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ORBITA NÚCLEO COMPARTILHADO                                        │   │
│  │  •registry • workspace • security • approvals • audit • process     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Persistência                                                       │   │
│  │  • config.json (%PROGRAMDATA%\ORBITA\config.json)                   │   │
│  │  • audit.jsonl (%PROGRAMDATA%\ORBITA\audit.jsonl)                   │   │
│  │  • logs/ (%PROGRAMDATA%\ORBITA\logs\)                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ARQUIVOS                                                                │
│  • workspaceRoot (caminho absoluto)                                        │
│  • servico.reg (SCM)                                                     │
│  • logs/orbita-service.log                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Ciclo de vida do serviço

```
[Instalação] → [Registro SCM] → [Inicialização] → [Roda] → [Monitoramento]
       │              │              │              │             │
       ▼              ▼              ▼              ▼             ▼
  Node  │       sc.exe create  │    node        │  Health       │  Logs
  Service│     (auto start)     │  service     │  check        │  persistent
  (npm  │                      │  starts      │  /health      │  + Event
   install)                                          │               │  Viewer
                                                     ▼
                                              [Falha / Recuperação]
                                              • restart automatico (SCM)
                                              • logs de erro
                                              • health check
                                              ▼
                                              [Encerramento gracioso]
                                              • shutdown endpoint
                                              • finalização de processos
                                              • desregisto do serviço
```

---

## 4. FLUXO DE DADOS

### 4.1 Fluxo de dados do modo A (STDIO)

```
┌──────────────┐   │  STDIN    ┌───────────────────────────┐   │  STDOUT   │
│ ChatGPT      │ ───┤           │  JSON-RPC request         │ ───┤           │
│ Desktop      │    │           │                           │    │           │
│ (host MCP)   │ ───┤           │  initialize (id=1)        │ ───┤           │
└──────────────┘    │           │  notifications/initialized│    │           │
                    │           │  tools/list (id=3)        │ ───┤           │
                    │           │  tools/call (id=4)        │ ───┤           │
                    │           └───────────────────────────┘    │           │
                    │                                          │            │
                    ▼                                          ▼            │
┌───────────────────────────────────────────────────────────────────────────┐ │
│  ORBITA MCP SERVER (Node.js)                                             │ │
│  • analyze JSON-RPC on stdin                                           │ │
│  • invoke tools (registerOrbitaTools)                                  │ │
│  • audit log (audit.mjs)                                               │ │
│  • return JSON-RPC response (stdout)                                   │ │
└───────────────────────────────────────────────────────────────────────────┘ │
                    │                                          │            │
                    │  STDOUT (JSON-RPC only)                  │            │
                    ▼                                          ▼            │
┌──────────────┐   │  STDIN (echo)  ┌───────────────────────────┐   │  STDOUT   │
│ ChatGPT      │ ───┤                  │  response JSON-RPC      │ ───┤           │
│ Desktop      │    │                  │  (initialize, tools/   │    │           │
│ (host MCP)   │ ───┤                  │   list, tools/call)   │ ───┤           │
└──────────────┘    │                  └───────────────────────────┘    │           │
                    │                                          │            │
                    ▼                                          ▼            │
               STDOUT (JSON-RPC)                             STDERR (logs)  │
```

### 4.2 Fluxo de dados do modo B (Serviço HTTP)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CLIENTE REMOTO (HTTP/HTTPS)                                              │
│  • Authorization: Bearer <token>                                          │
│  • POST /mcp { jsonrpc: "2.0", id: 1, method: "tools/list", params: {} }  │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ORBITA SERVICE (Node.js HTTP Server)                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Middleware:                                                        │   │
│  │  • Auth (Bearer token / certificado)                                │   │
│  │  • CORS (same-origin policy)                                        │   │
│  │  • Rate limiting (limite de requisições)                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Routing:                                                           │   │
│  │  • GET  /health    → health check (200 OK)                          │   │
│  │  • POST /mcp      → Streamable HTTP (JSON-RPC)                      │   │
│  │  • GET  /mcp (log) → log do serviço                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ORBITA NÚCLEO COMPARTILHADO                                        │   │
│  │  • tools.mjs (11 ferramentas)                                       │   │
│  │  • security.mjs (guards)                                            │   │
│  │  • approvals.mjs (tokens)                                           │   │
│  │  • audit.mjs (JSONL)                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  RESPOSTAS                                                               │
│  • JSON-RPC (tools/list, tools/call)                                     │
│  • Logs (debug, erros)                                                   │
│  • Health endpoint (200 OK)                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Fluxo de dados do modo B — Autenticação

```
┌──────────────┐   ┌──────────────┐
│  Cliente     │   │  Token       │
│  (remoto)    │   │  (Bearer)    │
└──────────────┘   └──────────────┘
        │                  │
        ▼                  ▼
┌────────────────┐  ┌────────────────┐
│  Request       │  │  Autenticação  │
│  /mcp          │  │  (verificar)   │
│  (JSON-RPC)    │  │  - token válido│
│  (Authorization│  │  - expira?     │
│   header)      │  │  - escopo?     │
└────────────────┘  └────────────────┘
        │                  │
        ▼                  ▼
┌────────────────┐  ┌────────────────┐
│  Autenticado   │  │  Rejeitar      │
│  (prosseguir)  │  │  401 Unauthorized│
└────────────────┘  └────────────────┘
```

---

## 5. DIAGRAMA DE COMPONENTES (MODO B)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ORBITA SERVICE (serviço Windows)                                          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Camada de rede                                                      │    │
│  │  ┌──────────────────────┐  ┌──────────────────────┐                │    │
│  │  │ HTTP / HTTPS         │  │ WebSockets (futuro)  │                │    │
│  │  │ GET /health          │  │ POST /sync (opcional)│                │    │
│  │  │ POST /mcp            │  │                      │                │    │
│  │  │ GET  /mcp (log)      │  │                      │                │    │
│  │  └──────────────────────┘  └──────────────────────┘                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Camada de segurança                                               │    │
│  │  ┌──────────────────────┐  ┌──────────────────────┐                │    │
│  │  │ Autenticação         │  │ Autorização        │                │    │
│  │  │ • Bearer token       │  │ • readOnlyHint     │                │    │
│  │  │ • Certificado        │  │ • destructiveHint  │                │    │
│  │  │ • API key (legacy)   │  │ • openWorldHint    │                │    │
│  │  └──────────────────────┘  └──────────────────────┘                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ORBITA NÚCLEO COMPARTILHADO (reutiliza código existente)          │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │    │
│  │  │ registry     │  │ state        │  │ security     │             │    │
│  │  │ (tools)      │  │ (workspace)  │  │ (guards)     │             │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │    │
│  │  │ approvals    │  │ audit        │  │ process      │             │    │
│  │  │ (tokens)     │  │ (JSONL)      │  │ (execução)   │             │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Camada de persistência                                            │    │
│  │  • config.json (%PROGRAMDATA%\ORBITA\config.json)                  │    │
│  │  • audit.jsonl (%PROGRAMDATA%\ORBITA\audit.jsonl)                  │    │
│  │  • logs/ (%PROGRAMDATA%\ORBITA\logs\)                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Gestão do serviço (SCM)                                           │    │
│  │  • sc.exe create / start / stop / delete                           │    │
│  │  • restart on failure                                              │    │
│  │  • recovery policy (restart delay)                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Monitoramento                                                     │    │
│  │  • Health endpoint (/health)                                       │    │
│  │  • Log file (orbita-service.log)                                   │    │
│  │  • Event Viewer integration                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. DIAGRAMA DE FLOW (MODO B)

```
┌─────────────┐
│  Cliente    │
│  remoto     │
└──────┬──────┘
       │
       │ 1. Autentica (Bearer token)
       ▼
┌──────────────────┐
│ /auth endpoint   │
│ Verificar token  │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
   OK       invalid
    │         │
    ▼         ▼
┌──────────┐ ┌──────────────┐
│ /mcp     │ │ 401 Unauthorized│
│ (JSON-RPC)│ └──────────────┘
└──────────┘
    │
    │ 3. Validar método + autorização
    ▼
┌──────────────────┐
│ Método válido?   │
│ Política de aprovação?│
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
   OK       inválido
    │         │
    ▼         ▼
┌──────────┐ ┌──────────────┐
│ Executar │ │ 403/405 error │
│ handler  │ └──────────────┘
└────┬─────┘
     │
     ▼
┌──────────────────┐
│ Executar ferramenta│
│ (registerOrbitaTools)│
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ Reverter auditoria?│
│ (audit.mjs)      │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ Responder JSON-RPC  │
│ (200 OK)          │
└──────────────────┘
```

---

## 7. DIAGRAMA DE CICLO DE VIDA DO SERVIÇO

```
[Instalação] ──► [RegistroSCM] ──► [Inicialização] ──► [Roda] ──► [Monitoramento]
       │                │                │            │           │
       ▼                ▼                ▼            ▼           ▼
  Copy  │         sc.exe create  │     node       │  Health     │  Logs
  files │        (auto-start)    │  service     │  /health    │  persistent
         │                      │              │             │  + Event
         ▼                      ▼              ▼             ▼     Viewer
   [Backup] → [Clean]  │        │            │           │        │
                        ▼      │            │           │        ▼
                   [Desinstalação] ◄── [Encerramento gracioso] ◄── [Recuperação]
```

---

## 8. DIAGRAMA DE STREAMING (MODO B — HTTP) — (opcional)

```
┌──────────────┐
│ Cliente      │
│ (Streamable) │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ /mcp (POST)          │
│ Accept: text/event-stream│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Server-Sent Events   │
│ SSE (text/event-stream)│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Resposta streaming   │
│ (JSON-RPC chunks)    │
└──────────────────────┘
```

---

## 9. DIAGRAMA DE COMUNICAÇÃO (MODO A vs B)

```
MODO A — STDIO (local)
┌──────────────┐   │
│ Cliente MCP  │   │ node src/index.mjs
│ (ChatGPT)    │ ──┤ (STDIN/STDOUT)
└──────────────┘   │
                   ▼
         ORBITA MCP SERVER (STDIO)
                   │
                   ▼
         ORBITA NÚCLEO
                   │
                   ▼
         Arquivos / sistema

MODO B — Serviço Windows
┌──────────────┐   │
│ Cliente      │   │ HTTPS POST /mcp
│ remoto       │ ──┤ (HTTP/2)
└──────────────┘   │
                   ▼
         ORBITA SERVICE (HTTP)
                   │
                   ▼
         ORBITA NÚCLEO
                   │
                   ▼
         Persistência (config.json, audit.jsonl, logs/)
```

---

## 10. RESUMO

| Modo | Transporte | Número de ferramentas | Autenticação | Persistência | Monitoramento |
|---|---|---|---|---|---|
| **A — MCP STDIO** | STDIO (stdin/stdout) | 11 | Nenhuma (relie no sandbox do host) | config.json, audit.jsonl | Logs (stderr) |
| **B — Serviço Windows** | Streamable HTTP | 11 | Bearer token/certificado | config.json, audit.jsonl, logs/ | Health endpoint, Event Viewer |

---

**Documento gerado em 31/10/2026.**
