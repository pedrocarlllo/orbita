# ORBITA_ESPECIFICACAO_COMPLETA_PLUGIN_CHATGPT.md

**Versão do projeto:** 0.1.0  
**Arquivo-fonte:** `C:\ORBITA-Universal-Plugin-Windows-0.1.0\orbita-agent`  
**Última recolha:** 31/10/2026  
**Estado:** Inspectado, não modificado.

---

## 1. Identificação do Projeto

| Campo | Valor |
|---|---|
| Nome oficial | ORBITA — Agente Universal Local para Windows |
| Versão do projeto | 0.1.0 |
| Runtime | Windows nativo + PowerShell 5.1+ |
| Protocolo | MCP STDIO (JSON-RPC) |
| Idioma | Português (diálogos e mensagens em PT-BR) |
| Licença | MIT (indicada em `.codex-plugin/plugin.json`) |
| Requisito mínimo | Node.js 22 ou superior (LTS recomendado) |

### Objetivo e funcionalidades
ORBITA é um agente universal local instalado fora dos projetos (`%USERPROFILE%\plugins\orbita-agent`). Ele não pertence a nenhum projeto específico. O usuário indica uma pasta de projeto (caminho absoluto) e ORBITA muda o workspace ativo para essa pasta, com limites de leitura, pesquisa e escrita aplicados.

A partir do workspace ativo, ORBITA expõe um conjunto de ferramentas MCP (`orbita_*`) que permitem:
- Consulta de status e workspace ativo.
- Listagem de arquivos e pastas.
- Leitura de arquivos de texto.
- Busca textual em arquivos.
- Inspeção de projeto (detecção de linguagens/manifests).
- Consulta de estado e diffs Git (somente leitura).
- Preparação de alterações de arquivo (prévia + token de uma única vez).
- Aplicação de alteração aprovada (gravação atômica + backup + hash-base).
- Execução de tarefas de teste/build predefinidas (apenas tarefas suportadas).

---

## 2. Arquitetura do Agente

### Fluxo geral
```
ChatGPT Desktop / Codex
   │  plugin local + skills + MCP STDIO (JSON-RPC)
   ▼
ORBITA MCP Server (Node.js 22+)
   │  tools registradas via Zod 4 + McpServer
   ├── Tool Registry (Zod 4)
   ├── Workspace & Path Guard (security.mjs)
   ├── Read/Search/Project Inspector (workspace.mjs)
   ├── Git Read-only Adapter (runProcess)
   ├── Change Preview + One-time Approval Token (approvals.mjs)
   ├── Atomic Writer + Backup (tools.mjs)
   ├── Fixed Task Runner (process.mjs)
   ├── Audit JSONL (audit.mjs)
   └── Config Store (state.mjs)
```

### Como funciona o núcleo
1. **Recebimento:** ChatGPT Desktop/Codex lança o processo MCP STDIO (`node server/src/index.mjs`) e envia mensagens JSON-RPC pelo stdin/stdout. A saída do servidor vai para **stderr**; a saída do protocolo JSON-RPC deve permanecer em **stdout**.
2. **Inicialização:** O `index.mjs` cria uma instância de `OrbitaState`, um `AuditLog` e um `ApprovalStore`, registra 11 ferramentas via `registerOrbitaTools` e chama `serveStdio(createServer)`.
3. **Interpretação:** O servidor não interpreta prompts diretamente. Ele expõe ferramentas HTTP-independentes; o host MCP (ChatGPT/Codex) traduz as ações do usuário em chamadas a essas ferramentas.
4. **Plano de tarefas:** ORBITA não tem um "planejador" de tarefas interno. O fluxo é:
   - `orbita_status` → confirma workspace ativo e limites.
   - `orbita_list_files`, `orbita_read_file`, `orbita_search_files`, `orbita_inspect_project` → reconhece o projeto.
   - `orbita_git_status`, `orbita_git_diff` → informa estado e mudanças.
   - `orbita_prepare_file_change` → gera prévia com hash-base e token de uso único.
   - `orbita_apply_file_change(token)` → aplica a alteração após autorização explícita.
   - `orbita_run_project_task(task)` → executa tarefas predefinidas (npm-test/build/lint/typecheck, python-pytest, dotnet-test/build, go-test, cargo-test/build).
5. **Resposta:** Cada ferramenta retorna um objeto JSON com `content: [{ type: 'text', text: ... }]` e, opcionalmente, `isError: true`. O host MCP formata a saída para o usuário.
6. **Contexto e memória:** O estado do servidor (workspaceRoot, config, dataDir) é mantido **apenas na memória do processo MCP**. O `config.json` é persistido em `%LOCALAPPDATA%\ORBITA\config.json` e carregado em cada inicialização. O `audit.jsonl` guarda métricas de ações. **Não há banco de dados, embeddings ou arquiteto de memória** no ORBITA 0.1.0.
7. **Gerenciamento de erros:** Cada ferramenta envolve o handler em `try/catch`, captura `error.message` (ou `String(error)`), registra no `audit.jsonl` com `outcome: 'error'` e retorna `asTextResult({ error, tool })` com `isError: true`.

---

## 3. MCP — MODEL CONTEXT PROTOCOL

| Item | Descrição |
|---|---|
| Servidor MCP próprio? | **Sim.** @orbita/local-mcp-server |
| Linguagem | Node.js 22+ (ESM, `.mjs`) |
| Localização do código | `server/src/index.mjs` (entrypoint), `server/src/tools.mjs` (registro de ferramentas), `server/src/security.mjs`, `state.mjs`, `workspace.mjs`, `process.mjs`, `approvals.mjs`, `audit.mjs` |
| Comando de inicialização | `node server/src/index.mjs` (ou via `npm start` no diretório `server`) |
| Transporte | **stdio** (JSON-RCP sobre stdin/stdout). **Não** SSE, **não** Streamable HTTP. |
| SDK | `@modelcontextprotocol/server` 2.4.0 (`McpServer`, `registerTool`, `serveStdio`) |
| Zod | 4.6.7 (`zod/v4` subpath import) |
| Ferramentas MCP implementadas | 19 |
| Autenticação | **Não há autenticação MCP.** O servidor é definido pelo host MCP (ChatGPT Desktop/Codex), que aplica sandbox e política de aprovação. |
| Permissões | Contadas por anotações `readOnlyHint`, `destructiveHint`, `openWorldHint`. Ferramentas de escrita (`orbita_set_workspace_root`, `orbita_prepare_file_change`, `orbita_apply_file_change`, `orbita_run_project_task`) têm `destructiveHint: true` ou `openWorldHint: true` e exigem aprovação do host MCP no ChatGPT/Codex. |

### Ferramentas MCP e contratos

#### 1. orbita_status
- **InputSchema:** `z.object({})` (nenhum parâmetro)
- **Saída:** objeto com `name`, `version`, `runtime`, `platform`, `workspaceRoot`, `dataDirectory`, `limits` (maxReadBytes, maxWriteBytes, maxSearchFiles, commandTimeoutMs), `protections` (array de strings).
- **Efeito:** nenhum.

#### 2. orbita_set_workspace_root
- **InputSchema:** `{ path: z.string().min(3).max(1024) }`
- **Saída:** `{ workspaceRoot: string, message: string }`
- **Efeito:** altera o workspace ativo. Exige aprovação do host MCP (destructiveHint: true). Rejeita caminhos absolutos, raízes de unidade e paths sensíveis.

#### 3. orbita_list_files
- **InputSchema:** `{ path?: string, limit?: number, maxDepth?: number }`
- **Saída:** `{ items: [{ path, type }], visited, truncated }`
- **Efeito:** leitura.

#### 4. orbita_read_file
- **InputSchema:** `{ path: z.string().min(1).max(1024) }`
- **Saída:** `{ path, bytes, truncated, content }`
- **Efeito:** leitura. Bloqueia binários, arquivos sensíveis e caminhos fora do workspace. Limita a 28_000 caracteres.

#### 5. orbita_search_files
- **InputSchema:** `{ query, maxFiles?, maxResults? }` (query é z.string().min(1).max(200))
- **Saída:** `{ query, matches: [{ path, line, snippet }], filesScanned, resultsTruncated }`
- **Efeito:** busca literal por substring (case-insensitive) em todos os arquivos não sensíveis.

#### 6. orbita_inspect_project
- **InputSchema:** `z.object({})`
- **Saída:** `{ workspaceRoot, detectedProjectTypes, manifests, rootFiles, packageInfo, scannedEntries, listingTruncated }`
- **Efeito:** leitura. Detecta linguagens, manifests e scripts npm.

#### 7. orbita_git_status
- **InputSchema:** `z.object({})`
- **Saída:** `{ output: string }` (stdout do `git status --short --branch -- .`)
- **Efeito:** leitura.

#### 8. orbita_git_diff
- **InputSchema:** `{ maxChars: z.number().int().min(1000).max(30000).default(18000) }`
- **Saída:** `{ files, diff, truncated }`
- **Efeito:** leitura. Mostra diffs unstaged e staged, excluindo caminhos sensíveis.

#### 9. orbita_prepare_file_change
- **InputSchema:** `{ path, content }` (content `z.string().max(1_100_000)`)
- **Saída:** `{ path, operation, token, expiresInSeconds, bytesBefore, bytesAfter, sha256Before, sha256After, before: { lines, preview, truncated }, after, nextStep }`
- **Efeito:** não grava. Cria prévia, calcula SHA-256, mantém a proposta na memória do processo (ApprovalStore).

#### 10. orbita_apply_file_change
- **InputSchema:** `{ token: z.string().uuid() }`
- **Saída:** `{ path, operation, bytesWritten, sha256, backupPath, verified }`
- **Efeito:** grava. Revalida caminho e hash-base, cria backup, escreve para `.tmp` e faz `rename` (write atômica). Expira em 5 minutos.

#### 11. orbita_run_project_task
- **InputSchema:** `{ task: z.enum([...]) }`
- **Tarefas suportadas:**
  - `npm-test` → `['test', ['test']]`
  - `npm-build` → `['build', ['run', 'build']]`
  - `npm-lint` → `['lint', ['run', 'lint']]`
  - `npm-typecheck` → `['typecheck', ['run', 'typecheck']]`
  - `python-pytest` → `{ command: 'py' | 'python3', args: ['-m', 'pytest', '-q'] }`
  - `dotnet-test` → `['test', '--nologo']`
  - `dotnet-build` → `['build', '--nologo']`
  - `go-test` → `{ command: 'go', args: ['test', './...'] }`
  - `cargo-test` → `{ command: 'cargo', args: ['test'] }`
  - `cargo-build` → `{ command: 'cargo', args: ['build'] }`
- **Saída:** `{ task, command, exitCode, success, timedOut, durationMs, stdout, stderr }`
- **Efeito:** executa tarefa predefinida. Empacotamento `npm.cmd` no Windows (`ComSpec /d /s /c`), `shell: false` no child process, env limitado (`SAFE_ENV_KEYS`).

---

## 4. Inventário de Ferramentas

| # | Ferramenta | Descrição | Parâmetros | Tipos de dados | Resultado esperado | Arquivos responsáveis | Dependências | Permissões |
|---|---|---|---|---|---|---|---|---|
| 1 | `orbita_status` | Status e workspace ativo. | nenhum | — | `{ name, version, runtime, platform, workspaceRoot, dataDirectory, limits, protections }` | `tools.mjs`, `state.mjs`, `security.mjs`, `approvals.mjs` | zod | leitura |
| 2 | `orbita_set_workspace_root` | Define pasta de projeto por caminho absoluto. | `path: string` (3-1024) | string | `{ workspaceRoot, message }` | `state.mjs`, `security.mjs` | node:fs/promises | leitura+escrita; aprovação de host |
| 3 | `orbita_list_files` | Lista arquivos e pastas no workspace. | `path?: string`, `limit?: number`, `maxDepth?: number` | string, number, number | `{ items, visited, truncated }` | `workspace.mjs` | node:fs/promises | leitura |
| 4 | `orbita_read_file` | Lê arquivo de texto no workspace. | `path: string` (1-1024) | string | `{ path, bytes, truncated, content }` | `security.mjs`, `workspace.mjs` | node:fs/promises | leitura |
| 5 | `orbita_search_files` | Busca textual literal em arquivos. | `query: string`, `maxFiles?, maxResults?` | string, number, number | `{ query, matches, filesScanned, resultsTruncated }` | `workspace.mjs` | node:fs/promises | leitura |
| 6 | `orbita_inspect_project` | Detecta linguagens, manifests e scripts npm. | nenhum | — | `{ workspaceRoot, detectedProjectTypes, manifests, rootFiles, packageInfo, scannedEntries, listingTruncated }` | `workspace.mjs` | node:fs/promises | leitura |
| 7 | `orbita_git_status` | Consulta estado Git. | nenhum | — | `{ output: string }` | `tools.mjs` | node:child_process | leitura |
| 8 | `orbita_git_diff` | Diffs staged/unstaged excluindo caminhos sensíveis. | `maxChars?: number` | number | `{ files, diff, truncated }` | `tools.mjs` | node:child_process, security.mjs | leitura |
| 9 | `orbita_prepare_file_change` | Cria prévia sem gravar. | `path: string`, `content: string` (max 1.1MB) | string, string | `{ path, operation, token, expiresInSeconds, bytesBefore, bytesAfter, sha256Before, sha256After, before, after, nextStep }` | `security.mjs`, `approvals.mjs`, `workspace.mjs` | node:fs/promises, crypto | escrita (prévia) |
| 10 | `orbita_apply_file_change` | Aplica prévia. Consome token único. | `token: string` (UUID) | string | `{ path, operation, bytesWritten, sha256, backupPath, verified }` | `security.mjs`, `approvals.mjs`, `state.mjs` | node:fs/promises, crypto | escrita |
| 11 | `orbita_run_project_task` | Executa tarefa predefinida. | `task: 'npm-test' | 'npm-build' | 'npm-lint' | 'npm-typecheck' | 'python-pytest' | 'dotnet-test' | 'dotnet-build' | 'go-test' | 'cargo-test' | 'cargo-build'` | enum | `{ task, command, exitCode, success, timedOut, durationMs, stdout, stderr }` | `tools.mjs`, `process.mjs`, `workspace.mjs` | node:child_process | escrita/execução |

**Nota:** as tecnologias suportadas nas tarefas de build/test são: Node.js (npm), Python, .NET, Go e Rust. Não há shell arbitrário.

---

## 5. API e Comunicação

| Aspecto | Descrição |
|---|---|
| Transporte | **STDIO** (JSON-RPC sobre stdin/stdout). |
| Autenticação | **Não há autenticação MCP.** O host (ChatGPT Desktop/Codex) aplica sandbox e política de aprovação. |
| Método HTTP | N/A (não há HTTP). |
| Endpoints | N/A. |
| Estrutura de requisição | JSON-RPC 2.0 via stdin. |
| Estrutura de resposta | Objeto JSON com `content: [{ type: 'text', text: string }]` e opcional `isError: true`. |
| Variáveis de ambiente | `ORBITA_DATA_DIR` (sobrescreve `%LOCALAPPDATA%\ORBITA`), `ORBITA_WORKSPACE_ROOT` (sobrescreve workspace padrão). |
| Configurações necessárias | `server/package.json` (dependencies: @modelcontextprotocol/server 2.4.0, zod 4.6.7). |
| WebSockets | N/A. |

---

## 6. Inteligência Artificial

| Item | Descrição |
|---|---|
| Integração com LLM? | **Não.** O ORBITA é um agente local que expõe ferramentas MCP. O LLM é fornecido pelo ChatGPT/Codex (host). |
| Provedores suportados | Não definido no ORBITA. Depende do host (ChatGPT/Codex). |
| Modelos | Não definido. |
| Seleção de modelos | Não implementada no ORBITA. |
| Processamento de contexto | O host (ChatGPT/Codex) gerencia o contexto. |
| Execução de chamadas de ferramentas | ORBITA expõe 11 ferramentas MCP; o host as chama. |
| Agentes especializados | **Não.** ORBITA não tem subagentes. O modelo de linguagem do host executa o fluxo. |

---

## 7. Memória e Conhecimento

| Item | Descrição |
|---|---|
| Sistema de memória | **Nenhum** dentro do ORBITA. O estado é mantido na memória do processo MCP. |
| Persistência | `%LOCALAPPDATA%\ORBITA\config.json` (Windows). |
| Banco de dados | **Não há** banco de dados. |
| Recuperação de informações | `orbita_search_files` faz busca textual (case-insensitive) em arquivos não sensíveis, com limites de files, bytes e resultados. Não há embeddings nem busca semântica. |
| Armazenamento de arquivos | Arquivos de projeto são consultados via `orbita_read_file`, `orbita_list_files`, etc. O ORBITA não grava arquivos de projeto sem prévia e autorização. |
| Limitações | Memória persistente apenas via `config.json` (limites, workspace). Logs via `audit.jsonl` (apenas metadados). Sem embeddings, RAG, memoização ou vetores. |

---

## 8. Segurança

### Controles implementados
| Ameaça | Controle |
|---|---|
| Path traversal | Apenas caminhos relativos ao workspace; `..` rejeitado. |
| Symlink escape | Resolve caminhos reais e verifica contenção no workspace. |
| Exposição de segredo | Bloqueio de `.env*`, `.ssh`, `.git`, `node_modules`, tokens, credenciais, extensões de chave/certificado (`.pem`, `.key`, `.p12`, `.pfx`, `.keystore`, `.jks`). |
| Arquivo binário/grande | Detecção de NUL e limites de bytes (maxReadBytes 512KB, maxWriteBytes 1MB). |
| Escrita não autorizada | Prévia + token único + confirmação do host + hash-base. |
| Corrida entre prévia e gravação | SHA-256 do conteúdo atual conferido antes da escrita. |
| Corrupção no write | Arquivo temporário + rename; backup antes de substituir. |
| Execução arbitrária | Sem shell geral; enum fechado de tarefas. |
| Script de build malicioso | Aprovação do host antes da execução; aviso explícito. |
| Vazamento por log | Apenas metadados (action, outcome, path, task, bytes, etc.). |
| Flood de saída | Limites de tamanho (24KB stdout, 28KB prévia), arquivos (1500) e timeout (120s). |

### Limitações / risco residual
- Um teste/build autorizado pode executar código arbitrário definido no projeto, consumir rede, modificar dados ou instalar hooks.
- A aprovação no host é barreira distinta do token interno. O token previne replay/acidentes, mas não substitui confirmação humana.
- O administrador da máquina e o usuário que controla a pasta do plugin podem modificar o código local.
- Bloqueio de segredos baseado em nomes/extensões não é scanner infalível.

---

## 9. Integração com ChatGPT

### Arquitetura recomendada
```
ChatGPT Desktop / Codex (host)
   │  plugin local + skills + MCP STDIO
   ▼
ORBITA MCP Server (Node.js 22+)
   │  11 ferramentas
   ▼
Workspace ativo (pasta do projeto)
```

### Configuração necessária
**via marketplace (~/.agents/plugins/marketplace.json):**
```json
{
  "name": "orbita-agent",
  "source": { "source": "local", "path": "C:\\ORBITA-Universal-Plugin-Windows-0.1.0\\orbita-agent" },
  "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
  "category": "Developer Tools"
}
```
E o servidor MCP registrado no `.mcp.json` (ou no marketplace principal):
```json
{
  "mcpServers": {
    "orbita-local": {
      "type": "stdio",
      "command": "node",
      "args": ["${PLUGIN_ROOT}/server/src/index.mjs"],
      "cwd": "${PLUGIN_ROOT}/server"
    }
  }
}
```
A variável `ORBITA_WORKSPACE_ROOT` pode ser definida para apontar para uma pasta de projeto. Caso não definida, o servidor começa em `%USERPROFILE%\.orbita\workspace`.

### Fluxo de uso
1. `orbita_status` → confirma workspace ativo e limites.
2. `orbita_inspect_project`, `orbita_list_files`, `orbita_git_status` → reconhece o projeto.
3. `orbita_read_file`, `orbita_search_files` → leituras necessárias.
4. `orbita_prepare_file_change` → prévia + token.
5. `orbita_apply_file_change(token)` → aplica após autorização.
6. `orbita_run_project_task(task)` → executa tarefa predefinida.

### Autenticação e autorização
- **Autenticação MCP:** não há. O host (ChatGPT Desktop/Codex) gerencia o sandbox e a política de aprovação.
- **Autorização:** ferramentas de escrita (`orbita_set_workspace_root`, `orbita_apply_file_change`, `orbita_run_project_task`) exigem aprovação do host MCP. Modo `writes` ou `prompt` recomendado.
- **Tokens de prévia:** 5 minutos, uso único, armazenados em memória (`ApprovalStore`).

### Gerenciamento de sessões
- Um workspace ativo por processo MCP. Pode ser trocado a qualquer momento via `orbita_set_workspace_root`. O estado persiste no `config.json` (limites) e no `audit.jsonl` (métricas).

### Limitações de compatibilidade
- O servidor STDIO funciona em clientes desktop que iniciam processos locais (ChatGPT Desktop/Codex). **Não disponibiliza acesso ao filesystem local no ChatGPT Web ou celular.**

---

## 10. Requisitos de Instalação

### Dependências
| Dependência | Versão |
|---|---|
| Node.js | 22.0.0 ou superior (LTS recomendado) |
| npm | inclui com Node.js LTS |
| Git | opcional (para ferramentas Git) |

### Dependências do servidor (npm)
| Pacote | Versão |
|---|---|
| @modelcontextprotocol/server | 2.4.0 |
| zod | 4.6.7 |

### Comandos de instalação
```powershell
# 1. Instalar Node.js LTS (se necessário)
winget install --id OpenJS.NodeJS.LTS

# 2. Extrair o pacote em uma pasta temporária

# 3. Executar instalador (do diretório do servidor ORBITA)
powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\Install-ORBITA.ps1
```

### Configuração do servidor
- O servidor inicia com `node server/src/index.mjs` (ou `npm start` no diretório `server`).
- Variáveis de ambiente:
  - `ORBITA_DATA_DIR` → caminho para `%LOCALAPPDATA%\ORBITA` ou `$HOME/.orbita`
  - `ORBITA_WORKSPACE_ROOT` → pasta de projeto ativa (sobrescreve o padrão)
- Arquivos de configuração:
  - `%LOCALAPPDATA%\ORBITA\config.json` (configuração do servidor, criado em primeira execução)
  - `%USERPROFILE%\.agents\plugins\marketplace.json` (marketplace local)
  - `%USERPROFILE%\.codex\config.toml` (política de aprovação MCP)

### Requisitos de hospedagem
- Windows nativo (processo MCP STDIO).
- Node.js 22+.
- Desktop (não web).

---

## 11. Testes e Confiabilidade

| Tipo | Estado |
|---|---|
| Testes unitários | Existem (`server/test/*.test.mjs`): approvals, process, security. |
| Cobertura | Não medida. |
| Testes MCP | Não há suíte de teste MCP. |
| Testes de integração | Não há. |
| Testes de segurança | Testes de unidade nos arquivos de segurança e processo. |
| Falhas conhecidas | Nenhuma documentada no código-fonte. |
| Funcionalidades incompletas | Nenhuma lista de testes unitários; a suíte é pequena. |

### Notas de reaproveitamento
- `server/test/approvals.test.mjs`: token de aprovação pode ser consumido uma vez e expira.
- `server/test/process.test.mjs`: ambiente seguro exclui chaves de API e NODE_OPTIONS.
- `server/test/security.test.mjs`: controle de path traversal, caminhos sensíveis e symlinks.

---

## 12. Documentação para Construção do Plugin

### Arquitetura proposta
```
ChatGPT Desktop / Codex
   │  plugin local + skills + MCP STDIO
   ▼
ORBITA MCP Server (Node.js 22+)
   ├── Tool Registry (Zod 4)
   ├── Workspace & Path Guard (security.mjs)
   ├── Read/Search/Project Inspector (workspace.mjs)
   ├── Git Read-only Adapter
   ├── Change Preview + One-time Approval Token
   ├── Atomic Writer + Backup
   ├── Fixed Task Runner
   ├── Audit JSONL
   └── Config Store
```

### Diagrama de comunicação
```
ChatGPT Desktop / Codex (host)
   │  MCP STDIO (JSON-RPC)
   ▼
ORBITA MCP Server (server/src/index.mjs)
   │  11 ferramentas
   ▼
Workspace ativo (pasta do projeto)
```

### Lista completa de ferramentas MCP
(inclui 11 ferramentas conforme lista no item 3 desta especificação)

### Contratos de entrada e saída
Para cada ferramenta, ver seção 3 desta especificação:
- `orbita_status`
- `orbita_set_workspace_root`
- `orbita_list_files`
- `orbita_read_file`
- `orbita_search_files`
- `orbita_inspect_project`
- `orbita_git_status`
- `orbita_git_diff`
- `orbita_prepare_file_change`
- `orbita_apply_file_change`
- `orbita_run_project_task`

### Manifesto e configuração necessários
- `.codex-plugin/plugin.json` (manifesto nativo do Codex)
- `.mcp.json` (configuração MCP do plugin local)
- `plugin.json` (manifesto portable Agent Plugins 1.0)
- `server/package.json` (dependências do servidor)
- `mcp.json` (servidor MCP)

### Estratégia de autenticação
- **Autenticação MCP:** não há. O host (ChatGPT Desktop/Codex) aplica sandbox e política de aprovação.
- **Autorização:** ferramentas de escrita exigem aprovação do host MCP. Modo `writes` ou `prompt` recomendado.
- **Tokens de prévia:** 5 minutos, uso único, armazenados em memória.

### Estrutura de diretórios recomendada
```
orbita-agent/
├── .mcp.json                 # config MCP local
├── .codex-plugin/
│   └── plugin.json           # manifesto nativo do Codex
├── plugin.json               # manifesto portable Agent Plugins 1.0
├── README.md
├── docs/
│   ├── install-windows.md
│   ├── security-model.md
│   └── technical-spec.md
├── scripts/
│   ├── Install-ORBITA.ps1
│   └── Uninstall-ORBITA.ps1
├── server/
│   ├── package.json
│   ├── src/
│   │   ├── index.mjs
│   │   ├── tools.mjs
│   │   ├── security.mjs
│   │   ├── state.mjs
│   │   ├── workspace.mjs
│   │   ├── process.mjs
│   │   ├── approvals.mjs
│   │   ├── audit.mjs
│   │   └── test/
│   │       ├── approvals.test.mjs
│   │       ├── process.test.mjs
│   │       └── security.test.mjs
│   └── test/
│       ├── approvals.test.mjs
│       ├── process.test.mjs
│       └── security.test.mjs
├── skills/
│   ├── orbita-engineering/
│   └── orbita-universal/
└── .gitignore
```

### Plano de implementação
1. **Instalar dependências:** `npm install` no diretório `server`.
2. **Validar sintaxe:** `node --check src/index.mjs`, `node --check src/tools.mjs`.
3. **Executar testes:** `node --test test/*.test.mjs` no diretório `server`.
4. **Registrar no marketplace:** unserialize `marketplace.json`, adicionar a entrada `orbita-agent`, escrever em UTF-8 sem BOM.
5. **Atualizar Codex config:** adicionar seção `[plugins."orbita-agent@orbita-local".mcp_servers.orbita-local]` com `enabled = true`, `default_tools_approval_mode = "writes"`.
6. **Reiniciar ChatGPT Desktop/Codex** e instalar o plugin.
7. **Validar:** `/mcp`, `orbita_status`, `orbita_inspect_project`, `orbita_set_workspace_root`.

### Critérios de aceitação
1. Manifestos JSON válidos.
2. Node reconhece a sintaxe de todos os módulos `.mjs`.
3. Testes unitários de path traversal, arquivos sensíveis, links simbólicos e tokens de aprovação passam.
4. Cliente ChatGPT Desktop lista as ferramentas do servidor.
5. Leitura fora do workspace e leitura de segredos são recusadas.
6. A gravação detecta alterações concorrentes e mantém backup.
7. Testes/builds exigem aprovação do host e não aceitam comando arbitrário.

---

## 13. Entrega Final

### 1. Recursos existentes e comprovados
- Servidor MCP STDIO (`@modelcontextprotocol/server` 2.4.0 + `zod` 4.6.7).
- 11 ferramentas MCP (`orbita_status`, `orbita_set_workspace_root`, `orbita_list_files`, `orbita_read_file`, `orbita_search_files`, `orbita_inspect_project`, `orbita_git_status`, `orbita_git_diff`, `orbita_prepare_file_change`, `orbita_apply_file_change`, `orbita_run_project_task`).
- Segurança: path traversal, symlink escape, bloqueio de segredos, write atômica, prévia + token, backup, timeout, limites de saída.
- Instalação via marketplace e Codex config.
- Arquitetura de segurança documentada.
- Testes unitários (security, process, approvals).

### 2. Recursos existentes, mas incompletos
- **Preparação de alteração:** suporta prévia, hash-base e token único, mas o cliente deve exibir a prévia e solicitar aprovação.
- **Documentação:** README.md, security-model.md, technical-spec.md, doxygen, skills, não há documento de especificação completa do plugin.

### 3. Recursos que precisam ser desenvolvidos
- **Busca semântica:** a busca atual é textual (case-insensitive).
- **Testes MCP:** não há suíte de teste MCP.
- **Testes de integração:** não há.
- **Documentação completa do plugin:** a solicitação pede um relatório técnico detalhado (esta especificação).
- **Autenticação MCP:** não há (a depender da necessidade).

### 4. Recursos que não existem
- **Execução arbitrária de shell:** rejeitada.
- **Operações de exclusão/renomeação:** não existentes.
- **Deploy/publish:** não suportados.
- **Conector remoto/SSE/Streamable HTTP:** não disponível (apenas STDIO).

### 5. Problemas e riscos
- **Node.js 22+:** exigência estrita; PHP/AutoHotKey não são suportados.
- **Autenticação MCP:** não há; o host aplica permissões.
- **Data directory:** `%LOCALAPPDATA%\ORBITA` pode não existir em sistemas onde o usuário não tem permissão de escrita.
- **Timeout:** 120s; scripts de build longos podem estourar.
- **Limitação de saída:** stdout 24KB, prévia 28KB, results 50.
- **Busca textual:** sem suporte a expressões regulares nem busca semântica.
- **Workspace único:** um workspace ativo por processo; troca requer nova instância ou estado no config.json.
- **Limitação de custos:** acesso ao filesystem local do host é restrito ao workspace ativo.

### 6. Arquitetura recomendada para integração
```
ChatGPT Desktop / Codex (host)
   │  plugin local + skills + MCP STDIO
   ▼
ORBITA MCP Server (Node.js 22+)
   ├── Tool Registry (Zod 4)
   ├── Workspace & Path Guard
   ├── Read/Search/Project Inspector
   ├── Git Read-only Adapter
   ├── Change Preview + One-time Approval Token
   ├── Atomic Writer + Backup
   ├── Fixed Task Runner
   ├── Audit JSONL
   └── Config Store
```

---

## Resumo Técnico

ORBITA é um **plugin MCP STDIO** para ChatGPT Desktop/Codex que fornece 11 ferramentas de engenharia de software seguras, operando sobre um **workspace ativo** definido pelo usuário. A arquitetura é simples: um servidor Node.js 22+ que registra ferramentas via Zod 4, com guardas de segurança para path traversal, segredos, escrita atômica e execution policy. A integração com ChatGPT é feita via marketplace local e `.mcp.json` com `type: stdio` e variável `${PLUGIN_ROOT}`. O ORBITA não é um LLM: ele expõe capacidades de leitura, pesquisa, análise, versionamento e controle de arquivos, sendo o LLM do host responsável pela inteligência. A segurança é baseada em whitelisting de caminhos, detecção de segredos, prévia + token único e gravação atômica. A instalação é sequencial: Node.js LTS → copiar pasta → `npm install` → marketplace + Codex config → reiniciar aplicativo. O plugin é portátil, trabalha com uma pasta de projeto por vez e promove a segurança ao bloquear acesso a arquivos sensíveis e caminhos fora do workspace.

---

**Documentado em:** `C:\ORBITA-Universal-Plugin-Windows-0.1.0\orbita-agent\ORBITA_ESPECIFICACAO_COMPLETA_PLUGIN_CHATGPT.md`