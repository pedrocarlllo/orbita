# ORBITA_ARQUITETURA_WINDOWS_SERVER.md

**Versão do documento:** 1.0
**Data:** 31/10/2026
**Projeto:** ORBITA Universal Windows Server
**Fase anterior:** FASE 0 — Diagnóstico concluído (relatório `ORBITA_DIAGNOSTICO_INICIAL.md`)
**Objectivo:** Propor uma arquitetura definitiva para transformar a ORBITA em uma plataforma compatível com Windows Server, preservando o projeto existente.

---

## 1. VISÃO GERAL

A ORBITA 0.1.0 é um plugin MCP STDIO (Node.js) que expõe 11 ferramentas de engenharia de software para hosts MCP como ChatGPT Desktop e Codex. Para atingir o objetivo de uma **plataforma Windows Server**, a arquitetura será dividida em **dois modos independentes**:

| Modo | Descrição | Transporte | Público-alvo |
|---|---|---|---|
| **A — MCP Local STDIO** | Integração com ChatGPT Desktop, Codex e outros hosts compatíveis | STDIO | Desktops com acesso a processos locais |
| **B — Serviço Windows Independente** | Servidor autónomo executável como serviço Windows | Streamable HTTP (recomendado) | Servidores Windows Server 2019/2022/2025 |

Ambos os modos partilham um **núcleo comum** que contém o registro de ferramentas, gestão de workspace, sistema de segurança, aprovações, auditoria e controle de processos. A duplicação de lógica entre os modos é evitada.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CLIENTES / HOSTS                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ ChatGPT      │  │ Codex        │  │ Outros hosts │  │ Serviços Web     │ │
│  │ Desktop      │  │ (Codex CLI)  │  │ MCP STDIO    │  │ (Streamable HTTP)│ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ORBITA WINDOWS SERVER                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  NÚCLEO COMPARTILHADO                                              │   │
│  │  • Registro de ferramentas                                       │   │
│  │  • Gestão de workspace                                           │   │
│  │  • Sistema de segurança (path, segredos, symlink, bytes)         │   │
│  │  • Sistema de aprovações (tokens de prévia)                      │   │
│  │  • Sistema de auditoria (JSONL)                                  │   │
│  │  • Controle de processos (execute, timeout, limites)             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────┐  ┌──────────────────────┐                       │
│  │  MODO A — MCP STDIO  │  │  MODO B — Serviço    │                       │
│  │                      │  │  Windows             │                       │
│  │  • steam: stdin/stdout│  │  • Serviço nativo    │                       │
│  │  • node src/index.mjs│  │  • State (SCM)       │                       │
│  │  • 11 ferramentas    │  │  • Logs persistentes │                       │
│  │  • Aprovações (MCP)  │  │  • Interceptação     │                       │
│  │  • Configuração .mcp.json│  │  • Transporte HTTP │                       │
│  └──────────────────────┘  └──────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. MODO A — MCP LOCAL STDIO

### 2.1 Objetivo

Manter a funcionalidade existente para integração com:

- **ChatGPT Desktop** (Windows/macOS/Linux)
- **Codex** (CLI)
- **Outros hosts MCP** compatíveis STDIO

### 2.2 Características

| Característica | Definição |
|---|---|
| Transporte | STDIO (stdin/stdout JSON-RPC) |
| Entry point | `server/src/index.mjs` |
| Diretório de trabalho | `server/` |
| Ferramentas expostas | 11 `orbita_*` |
| Aprovação | Política de aprovação do host MCP (configurável) |
| Auditoria | Registro JSONL no `%LOCALAPPDATA%\\ORBITA\\audit.jsonl` |
| Persistência | `config.json` no `%LOCALAPPDATA%\\ORBITA\\config.json` |
| Workspace ativo | Definido por `orbita_set_workspace_root` (na memória do processo) |

### 2.3 Fluxo de comunicação

```
ChatGPT Desktop / Codex
   │
   │ 1. Ler .mcp.json (≤ "mcpServers": { "orbita-local": { "type": "stdio", ... } })
   ▼
   │ 2. Lançar: node server/src/index.mjs (cwd = server/)
   ▼
   │ 3. Inicialização: initialize (id=1)
   ▼
   │ 4. Notificação: notifications/initialized (sem id)
   ▼
   │ 5. Descoberta: tools/list → 11 ferramentas
   ▼
   ▼
   ORBITA MCP SERVER (Node.js)
   │   • Inicializa McpServer
   │   • Registra 11 ferramentas via registerOrbitaTools
   │   • Chama serveStdio(createServer)
   ▼
   │
   │ 6. tools/call → execução de ferramenta
   ▼
   │
   ORBITA MCP SERVER (Node.js)
   │   • Executa handler
   │   • Regista audit
   │   • Retorna { content: [{type: "text", text}], isError? }
   ▼
   │
   │ 7. Resposta JSON-RPC
   ▼
ChatGPT Desktop / Codex
```

### 2.4 Estrutura de configuração existente (preservada)

| Arquivo | Papel |
|---|---|
| `.mcp.json` | Configuração MCP do plugin nativo (ChatGPT Desktop) |
| `mcp.json` | Configuração MCP standalone |
| `plugin.json` | Manifesto portable Agent Plugins 1.0 |
| `.codex-plugin/plugin.json` | Manifesto nativo do Codex |
| `server/src/index.mjs` | Entry point do servidor |
| `server/src/tools.mjs` | Registro das 11 ferramentas |

### 2.5 Limitações reconhecidas

- STDIO não suporta clientes remotos.
- Cuida de segurança apenas no level do sandbox do host (à aplicação da política de aprovação do host).
- Não há autenticação MCP no projeto atual.

---

## 3. MODO B — SERVIÇO WINDOWS INDEPENDENTE

### 3.1 Objetivo

Permitir que a ORBITA funcione como **serviço autónomo** no Windows Server, sem depender de um host MCP local.

### 3.2 Recursos exigidos

| Recurso | Implementação |
|---|---|
| Inicialização automática | Serviço Windows (SCM) ou script de inicialização |
| Execução em segundo plano | `net start orbita-service` ou configuração de serviço |
| Recuperação após falhas | Políticas de recuperação (restart on failure, restart delay) |
| Logs persistentes | Arquivo de log no `%PROGRAMDATA%\\ORBITA\\logs\\` |
| Monitoramento | Health check HTTP (Streamable HTTP) |
| Encerramento gracioso | Handshake `shutdown` + espera de finalização de processos |
| Configuração administrativa | Arquivo JSON em `%PROGRAMDATA%\\ORBITA\\config.json` |
| Controle de acesso | Permissões NTFS + autenticação de clientes remotos |
| Autenticação | Token Bearer ou certificado (projeto pendente implementação) |
| Autorização por ferramenta | Check das políticas de aprovação (leitura/escrita/execução) |
| Transporte MCP | Streamable HTTP (recomendado) ou STDIO via named pipe |
| Política de aprovação | Índice de escrita e execução (configurável) |

### 3.3 Arquitetura do serviço

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SERVIÇO WINDOWS (ORBITA SERVICE)                                           │
│  • Nó de serviço Windows (nssm / sc.exe / native)                          │
│  • Processo principal: node server/src/service.mjs                          │
│  • Endpoints:                                                             │
│    • GET  /health (health check)                                           │
│    • POST /mcp (Streamable HTTP — JSON-RPC)                               │
│    • POST /mcp (streamable)                                                │
│    • GET  /mcp (log)                                                       │
│  • Gestão de estado:                                                      │
│    • workspaceRoot (config)                                                │
│    • config (limites, permissões)                                          │
│    • audit (registros JSONL)                                               │
│  • Segurança:                                                             │
│    • Identidade do serviço (máximo de privilégios)                         │
│    • Permissões NTFS (só leitura do workspace)                             │
│    • Autenticação de cliente (Bearer token / certificado)                  │
│    • Autorização por ferramenta                                            │
│  • Monitoramento:                                                         │
│    • Health endpoint                                                     │
│    • Logs persistidos                                                    │
│    • Curva de recuo (restart policy)                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
     ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
     │ Workspace A  │        │ Workspace B  │        │ Workspace C  │
     │ (leitura)    │        │ (leitura)    │        │ (leitura)    │
     └──────────────┘        └──────────────┘        └──────────────┘
```

### 3.4 Estrutura de diretórios sugerida

```
ORBITA-WINDOWS-SERVER/
├── server/
│   ├── package.json
│   ├── src/
│   │   ├── index.mjs               # Entry point MODE A (STDIO)
│   │   ├── service.mjs             # Entry point MODE B (HTTP + serviço)
│   │   ├── tools.mjs               # Registro das 11 ferramentas
│   │   ├── security.mjs            # Guardas de segurança
│   │   ├── state.mjs               # Estado e workspace
│   │   ├── workspace.mjs           # Acesso aos arquivos
│   │   ├── process.mjs             # Execução de processos
│   │   ├── approvals.mjs           # Gestão de tokens de prévia
│   │   ├── audit.mjs               # Registro de auditoria
│   │   └── transport/
│   │       ├── streamable-http.mjs # Transporte Streamable HTTP
│   │       └── stdio.mjs           # Transporte STDIO (MODE A)
│   └── test/
│       ├── security.test.mjs
│       ├── approvals.test.mjs
│       ├── process.test.mjs
│       └── service.test.mjs        # Novos testes
├── service/
│   ├── orbita-service.psm1         # PowerShell module (install/uninstall)
│   └── orbita-service.sh           # Script de inicialização (Linux)
├── config/
│   ├── config.example.json         # Exemplo de configuração
│   └── policy.example.json         # Exemplo de política de aprovação
├── scripts/
│   ├── Install-ORBITA.ps1          # Instalador existente
│   ├── Uninstall-ORBITA.ps1        # Desinstalador existente
│   ├── Install-Service.ps1         # Registro do serviço Windows
│   ├── Uninstall-Service.ps1       # Despedida do serviço Windows
│   └── Set-Policy.ps1              # Atualização de políticas
├── logs/                           # Logs do serviço (persistence)
├── documentation/
├── ORBITA_ARQUITETURA_WINDOWS_SERVER.md
├── ORBITA_DIAGRAMA_ARQUITETURAL.md
├── ORBITA_DECISOES_ARQUITETURAIS.md
├── ORBITA_MATRIZ_COMPATIBILIDADE.md
├── ORBITA_PLANO_SEGURANCA.md
└── ORBITA_PLANO_IMPLEMENTACAO.md
```

---

## 4. NÚCLEO COMPARTILHADO

### 4.1 Componentes do núcleo

| Componente | Ficheiro existente | Papel |
|---|---|---|
| Registro de ferramentas | `server/src/tools.mjs` | Regista 11 ferramentas MCP |
| Gestão de workspace | `server/src/state.mjs` | Estado ativo, root do workspace |
| Sistema de segurança | `server/src/security.mjs` | Path, segredos, symlink, bytes |
| Aprovações | `server/src/approvals.mjs` | Tokens de prévia (UUID, uso único, 5 min) |
| Auditoria | `server/src/audit.mjs` | Registo JSONL de ações |
| Controle de processos | `server/src/process.mjs` | Execução segura de processos |
| Configuração | `server/src/state.mjs` | Limites e configurações |

### 4.2 Estrutura compartilhada

```
server/src/
├── core/
│   ├── registry.mjs      # Registro de ferramentas
│   ├── workspace.mjs     # Gestão de workspace
│   ├── security.mjs      # Sistema de segurança (já existente)
│   ├── approvals.mjs     # Sistema de aprovações (já existente)
│   ├── audit.mjs         # Auditoria (já existente)
│   └── process.mjs       # Controle de processos (já existente)
├── transport/
│   ├── stdio.mjs         # Transportes STDIO (MODE A)
│   └── streamable-http.mjs    # Transportes Streamable HTTP (MODE B)
├── index.mjs             # Entry point MODE A (STDIO)
├── service.mjs           # Entry point MODE B (HTTP + serviço)
└── tools.mjs             # Implementação das 11 ferramentas
```

### 4.3 Princípios de implementação

1. **Nenhuma duplicação:** o código compartilhado fica no `core/`. Não se duplica a lógica de segurança, aprovação e auditoria.
2. **Neutralidade do transport:** o núcleo não conhece a ordem de transportes; apenas expõe interfaces de que os transportes dependem.
3. **Singleton de estado:** o estado de workspace, config e audit é gerido por um singleton que os transportes consomem.
4. **Tool registry:** o registro de ferramentas é neutro para transportes; o server o itera para expor as ferramentas.

---

## 5. SEGURANÇA

### 5.1 Identidade e privilégios

| Entidade | Recomendação |
|---|---|
| Serviço Windows | Executar sob conta de baixo privilégio (não SYSTEM) |
| Permissões NTFS | Apenas leitura no workspace do usuário; escrita somente via API de aprovação |
| Isolamento entre usuários | Cada usuário tem workspace próprio; pasta separada |
| Isolamento entre workspaces | Cada workspace é um diretório isolado a partir do root do serviço |
| Proteção de credenciais | Nenhuma credencial armazenada no disco; apenas em memória ao executar |
| Autenticação dos clientes remotos | Bearer token ou certificado (não implementado atualmente; projeto pendente) |
| Autorização por ferramenta | Check das políticas de aprovação (readOnly/destructive/openWorld) |
| Proteção contra acesso externo indevido | Confined to localhost por default; configuração remota opcional |
| Registro de operações | Audit JSONL (já existente) |

### 5.2 Modelo de autorização

```
Cliente (remoto)
   │
   │ 1. Autentica (Bearer token / certificado)
   ▼
   │
   ORBITA SERVICE
   │
   │ 2. Verifica autenticação
   ▼
   │
   │ 3. Verifica autorização por ferramenta
   ▼
   │
   │ 4. Executa handler da ferramenta
   ▼
   │
   ORBITA SERVICE
   │   • Valida workspace
   │   • Verifica path traversal
   │   • Verica segredos
   │   • Executa operação
   │   • Regista auditoria
   ▼
   │
   RESPOSTA
```

### 5.3 Política de aprovação de escrita e execução

| Ferramenta | Leitura | Escrita | Execução | Aprovação |
|---|---|---|---|---|
| `orbita_status` | ✅ | ❌ | ❌ | Nenhuma |
| `orbita_list_files` | ✅ | ❌ | ❌ | Nenhuma |
| `orbita_read_file` | ✅ | ❌ | ❌ | Nenhuma |
| `orbita_search_files` | ✅ | ❌ | ❌ | Nenhuma |
| `orbita_inspect_project` | ✅ | ❌ | ❌ | Nenhuma |
| `orbita_git_status` | ✅ | ❌ | ❌ | Nenhuma |
| `orbita_git_diff` | ✅ | ❌ | ❌ | Nenhuma |
| `orbita_prepare_file_change` | ❌ | ⚠ Prévia | ❌ | Aprovação do host |
| `orbita_apply_file_change` | ❌ | ✅ | ❌ | Aprovação do host |
| `orbita_run_project_task` | ❌ | ❌ | ⚠️ Execução | Aprovação explícita |

---

## 6. COMPATIBILIDADE

### 6.1 Plataformas alvo

| Plataforma | Suporte | Notas |
|---|---|---|
| Windows Server 2019 | ✅ (teórica) | Node.js 22+ |
| Windows Server 2022 | ✅ | Node.js 22+ |
| Windows Server 2025 | ✅ | Node.js 22+ |
| Node.js 22+ | ✅ | Requisito mínimo |

### 6.2 Diferenças de compatibilidade

| Aspecto | Windows Server 2019 | Windows Server 2022 | Windows Server 2025 |
|---|---|---|---|
| Node.js LTS disponível | Sim | Sim | Sim |
| Windows Service nativo | Sim | Sim | Sim |
| PowerShell 5.1+ | Sim | Sim | Sim |
| Transporte HTTP/2 | Não (HTTP/1.1) | Sim (HTTP/2) | Sim |
| Security Baseline | Padrão | Mais restritivo | Mais restritivo |

### 6.3 Limitações

- **Testes efetivos:** a compatibilidade com Windows Server não foi testada neste ambiente. Identificar como não comprovada.
- **Transporte HTTP/2:** disponível no Windows Server 2022+; não em 2019.
- **Sandbox:** Windows Server não tem o mesmo level de sandbox do desktop; a autenticação de cliente é crítica.

---

## 7. INSTALADOR

### 7.1 Objetivo

Criar um instalador profissional que configure a ORBITA no Windows Server:

1. Verificação da versão do Windows.
2. Verificação do Node.js.
3. Instalação das dependências.
4. Configuração do diretório de dados.
5. Configuração do workspace.
6. Registro do serviço.
7. Configuração de inicialização.
8. Verificação de permissões.
9. Teste de funcionamento.
10. Desinstalação segura.

### 7.2 Perfil do instalador

| Fase | Ação |
|---|---|
| 1. Verificação | Windows (server), Node.js (≥ 22), PowerShell 5.1+ |
| 2. Preparação | Criar diretórios (%PROGRAMDATA%\\ORBITA) |
| 3. Instalação | Copiar arquivos; `npm install` no server/ |
| 4. Configuração | Criar config.json do serviço; definir workspace |
| 5. Registro | `sc.exe create` / PowerShell module (orbita-service) |
| 6. Inicialização | Start-Service; health check |
| 7. Backup | Backup do estado anterior |
| 8. Desinstalação | Parar serviço; remover registro; limpar arquivos |
| 9. Recuperação | Reinicialização automática; logs de erro |

### 7.3 Script PowerShell do serviço

```powershell
# Install-Service.ps1
# Registra o ORBITA como serviço Windows

param(
    [string]$ServiceName = "OrbitaService",
    [string]$DisplayName = "ORBITA Universal Server",
    [string]$NodePath = "node",
    [string]$ScriptPath = "C:\ProgramData\ORBITA\server\src\service.mjs",
    [string]$ConfigPath = "C:\ProgramData\ORBITA\config.json"
)

$ErrorActionPreference = "Stop"

# 1. Verificar Node.js
$nodeVersion = & $NodePath --version 2>$null
if ($nodeVersion -eq $null) {
    Write-Error "Node.js não encontrado. Instale o Node.js 22+."
    exit 1
}

# 2. Criar diretórios
New-Item -ItemType Directory -Force -Path "C:\ProgramData\ORBITA\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "C:\ProgramData\ORBITA\data" | Out-Null

# 3. Criar serviço
$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($service) {
    Stop-Service -Name $ServiceName -Force
    Remove-Service -Name $ServiceName
}

sc.exe create $ServiceName `
    binPath= """$NodePath"" ""$ScriptPath"" --config ""$ConfigPath""" `
    DisplayName= "$DisplayName" `
    StartType= auto `
    ErrorControl= normal

if ($LASTEXITCODE -ne 0) {
    Write-Error "Falha ao registrar o serviço."
    exit 1
}

# 4. Iniciar
Start-Service -Name $ServiceName

# 5. Verificar saúde
Start-Sleep -Seconds 3
$health = Invoke-WebRequest -Uri "http://localhost:3000/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
if ($health.StatusCode -eq 200) {
    Write-Host "Serviço ORBITA iniciado com sucesso."
} else {
    Write-Warning "Serviço iniciado, mas health check falhou."
}
```

---

## 8. DIAGRAMA DE COMUNICAÇÃO

### 8.1 Modo A — STDIO

```
ChatGPT Desktop / Codex
   │  .mcp.json → node server/src/index.mjs
   ▼
MCP STDIO (JSON-RPC over stdin/stdout)
   │
   ▼
ORBITA MCP SERVER
   │  tools/list → 11 ferramentas
   ▼
   │  tools/call → handler
   ▼
   │  audit
   ▼
   ORBITA NÚCLEO
```

### 8.2 Modo B — Serviço HTTP

```
Cliente Remoto (ChatGPT/Codex/Outro)
   │
   │  POST /mcp (Streamable HTTP)
   ▼
ORBITA SERVICE
   │  1. Autentica
   │  2. Autoriza
   │  3. Executa handler
   ▼
   │  4. Audit
   ▼
   ORBITA NÚCLEO
   │
   ▼
   RESPOSTA JSON-RPC
```

### 8.3 Ciclo de vida do serviço

```
[Instalação] → [Registro] → [Inicialização] → [Roda] → [Monitoramento]
                              │
                              ▼
                     [Recuperação após falha]
                              │
                              ▼
                     [Encerramento gracioso] → [Desinstalação]
```

---

## 9. DOCUMENTOS OBRIGATÓRIOS

| # | Documento | Descrição |
|---|---|---|
| 1 | `ORBITA_ARQUITETURA_WINDOWS_SERVER.md` | Arquitetura geral (este documento) |
| 2 | `ORBITA_DIAGRAMA_ARQUITETURAL.md` | Diagramas de componentes e fluxo de dados |
| 3 | `ORBITA_DECISOES_ARQUITETURAIS.md` | Decisões arquiteturais (alternativas, vantagens, justificativa) |
| 4 | `ORBITA_MATRIZ_COMPATIBILIDADE.md` | Matriz de compatibilidade (Windows Server 2019/2022/2025, Node.js 22+) |
| 5 | `ORBITA_PLANO_SEGURANCA.md` | Plano de segurança (identidade, privilégios, autenticação, autorização, auditoria) |
| 6 | `ORBITA_PLANO_IMPLEMENTACAO.md` | Plano de implementação dividido em etapas |

---

## 10. DECISÕES ARQUITETURAIS

### 10.1 Compartilhamento do núcleo

| Alternativa | Vantagens | Desvantagens | Justificativa |
|---|---|---|---|
| **A. Núcleo compartilhado** | Reutiliza lógica; menos duplicação; manutenção uniforme | Acoplamento mais forte | Preserva o código existente; reduz risco |
| B. Duas implementações separadas | Maior isolamento | Duplicação de código; maior manutenção | Não recomendada |

**Decisão:** adotar a **Alternativa A** — núcleo compartilhado no `core/`.

### 10.2 Transporte MCP

| Alternativa | Vantagens | Desvantagens | Justificativa |
|---|---|---|---|
| A. STDIO (MODE A) | Simples; já implementado | Não suporta remotos | Preservar funcionalidade |
| **B. Streamable HTTP** (MODE B) | Suporta remotos; HTTP/2; monitorável | Mais complexo | Recomendado para servidores |

**Decisão:** MODO A usa STDIO; MODO B usa **Streamable HTTP** (quando disponível, HTTP/2).

### 10.3 Serviço Windows

| Alternativa | Vantagens | Desvantagens | Justificativa |
|---|---|---|---|
| A. Serviço nativo (sc.exe) | Nativo do Windows; início automático | Maior complexidade | Melhor integração com o Windows |
| B. Script (task scheduler) | Simples | Menos robusto | Não recomendado |

**Decisão:** usar **Serviço nativo** via `sc.exe` ou PowerShell module.

### 10.4 Autenticação

| Alternativa | Vantagens | Desvantagens | Justificativa |
|---|---|---|---|
| A. Bearer token | Simples; flexível | Gerenciamento de rotation | Implementação futura |
| B. Certificado | Mais seguro | Maior complexidade | Recomendado para produção |

**Decisão:** projetar com Bearer token (ou certificado) na fase de produção.

### 10.5 Autorização por ferramenta

| Alternativa | Vantagens | Desvantagens | Justificativa |
|---|---|---|---|
| A. Utilizar anotações do MCP | Simples; integrado | Depende do host | Usar `readOnlyHint`, `destructiveHint` |
| B. Política própria | Mais granulares | Duplicação | Complementar às anotações |

**Decisão:** usar anotações MCP + política de aprovação explícita.

### 10.6 Logs

| Alternativa | Vantagens | Desvantagens | Justificativa |
|---|---|---|---|
| A. Console (STDOUT) | Simples | Não persistido | Não recomendado |
| B. Arquivos de log | Persistente; fácil análise | Ficheiros não rotacionados | Usar filesystem + rotacionamento |
| C. Event Viewer | Integrado com Windows | Menos acessível | Complementar |

**Decisão:** usar **arquivos de log** no `%PROGRAMDATA%\\ORBITA\\logs\\` + Event Viewer. Log de rotina: JSONL; monitor: arquivo de texto.

### 10.7 Persistência

| Alternativa | Vantagens | Desvantagens | Justificativa |
|---|---|---|---|
| A. Config.json (existente) | Já implementado | Simples | Manter padrão |
| B. Banco de dados | Escala | Sobrecarga | Não necessário para 0.1.0 |

**Decisão:** manter `config.json` + auditoria JSONL; não usar banco de dados.

### 10.8 Atualizações

| Alternativa | Vantagens | Desvantagens | Justificativa |
|---|---|---|---|
| A. Atualização manual | Simples | Requer reinício | Como padrão |
| B. Atualização automática | Menos interrupção | Complexidade | Fase futura |

**Decisão:** atualização manual com backup; fase futura contemplate.

### 10.9 Instalação

| Alternativa | Vantagens | Desvantagens | Justificativa |
|---|---|---|---|
| A. Install-ORBITA.ps1 | Existente e funcional | Instala plugins | Manter padrão |
| B. Install-Service.ps1 | Registra como serviço | Mais complexo | Estender para servidores |

**Decisão:** estender `Install-ORBITA.ps1` com modo `--service` para servidores.

### 10.10 Recuperação de falhas

| Alternativa | Vantagens | Desvantagens | Justificativa |
|---|---|---|---|
| A. Restart automático | Resiliência | Processo reinicia | Configuração do serviço |
| B. Logs de erro | Diagnóstico | Nenhum | Logs persistentes |
| C. Monitoramento | Proativo | Complexidade | Implementar health check |

**Decisão:** usar restart automático + health check + logs persistentes.

---

## 11. REGRAS

- Não modificar arquivos de código.
- Não instalar dependências.
- Não remover ferramentas.
- Não alterar configurações existentes.
- Não declarar compatibilidade sem evidência.
- Não inventar resultados.
- Preservar a arquitetura atual.
- Identificar riscos e dependências antes da implementação.

---

## 12. VEREDITO

A **FASE 1 — ARQUITETURA** será aprovada quando:

1. ✅ Os dois modos estiverem arquiteturalmente definidos.
2. ✅ O núcleo compartilhado estiver especificado.
3. ✅ O modelo de segurança estiver documentado.
4. ✅ O serviço Windows estiver projetado.
5. ✅ O transporte remoto estiver justificado.
6. ✅ O plano de implementação estiver dividido em etapas.
7. ✅ Os seis documentos estiverem entregues.

---

*Documento gerado em 31/10/2026. Base: ORBITA Universal Plugin Windows 0.1.0.*
