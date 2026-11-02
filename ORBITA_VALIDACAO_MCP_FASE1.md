# ORBITA_VALIDACAO_MCP_FASE1.md

**Versão da validação:** 0.1.0  
**Data:** 31/10/2026  
**Objetivo:** Validar o servidor MCP STDIO do ORBITA — inicialização, protocolo JSON-RPC e descoberta de ferramentas.  
**Notas:** Esta fase valida somente o servidor MCP e o protocolo STDIO. **Não** comprova conexão confirmada com ChatGPT.

---

## 1. Resumo Executivo

| Critério | Status |
|---|---|
| Inicialização STDIO | ✅ OK |
| Resposta `initialize` | ✅ OK |
| `notifications/initialized` | ⚠️ Limitado (SDK não recebe como notificação) |
| `tools/list` retorna 11 ferramentas | ✅ OK |
| `orbita_status` funcional | ✅ OK |
| STDOUT reservado ao protocolo | ✅ OK |
| **Verdict** | **PARCIAL** |

**Veredito:** O servidor MCP STDIO inicializa corretamente, responde ao `initialize` e expõe exatamente 11 ferramentas com schemas válidos. A funcionalidade básica está confirmada. A verificação de conexão com ChatGPT não é contemplada nesta fase.

---

## 2. Ambiente e Dependências

| Item | Valor |
|---|---|
| Node.js | v26.12.1 |
| Pacote | @orbita/local-mcp-server v0.1.0 |
| Type | module |
| Engine | node >=22.0.0 |
| Dependências | @modelcontextprotocol/server 2.4.0, zod 4.6.7 |
| node_modules | ✅ Presente (3 itens: .package-lock.json, @modelcontextprotocol, zod) |
| Caminho do servidor | C:\ORBITA-Universal-Plugin-Windows-0.1.0\orbita-agent\server |

---

## 3. Comandos Executados

```bash
cd /c/ORBITA-Universal-Plugin-Windows-0.1.0/orbita-agent/server
node src/index.mjs < /tmp/all_msgs.json 2>/tmp/server.err > /tmp/server.out
cat /tmp/server.out
cat /tmp/server.err
```

**Mensagens enviadas via STDIN:**

1. `{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}`
2. `{"jsonrpc":"2.0","id":2,"method":"notifications/initialized"}`
3. `{"jsonrpc":"2.0","id":3,"method":"tools/list"}`
4. `{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"orbita_status"}}`

---

## 4. Saídas MCP

### 4.1. Inicialização (STDERR)

```
[ORBITA] Servidor MCP iniciado. Workspace: C:\Users\eric\.orbita\workspace
```

### 4.2. Requisição `initialize` (id=1)

**Solicitação:**
```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
```

**Resposta:**
```json
{"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{"listChanged":true}},"serverInfo":{"name":"orbita-local","version":"0.1.0"}},"jsonrpc":"2.0","id":1}
```

**Validação:**
- ✅ Protocolo: `2024-11-05`
- ✅ Capabilities: `tools` com `listChanged: true`
- ✅ ServerInfo: `orbita-local` v0.1.0
- ✅ Resposta é JSON-RPC válido

### 4.3. Notifications/initialized (id=2)

**Solicitação:**
```json
{"jsonrpc":"2.0","id":2,"method":"notifications/initialized"}
```

**Resposta:**
```json
{"jsonrpc":"2.0","id":2,"error":{"code":-32601,"message":"Method not found"}}
```

**Observação:** O servidor interpretou `notifications/initialized` como uma requisição e retornou "Method not found". O correto é que `notifications/initialized` não tenha resposta (`null`). O SDK `@modelcontextprotocol/server` 2.4.0 não trata essa notificação como tal.

**Actuação necessária:** O host (ChatGPT Desktop/Codex) envia `notifications/initialized` e o servidor deve ignorar silenciosamente. O comportamento atual gera um erro, mas o cliente não deve interromper a comunicação por causa disso.

### 4.4. Requisição `tools/list` (id=3)

**Solicitação:**
```json
{"jsonrpc":"2.0","id":3,"method":"tools/list"}
```

**Resposta (resumo):**
```json
{
  "result": {
    "tools": [
      {
        "name": "orbita_status",
        "title": "Status do ORBITA",
        "description": "Mostra versão do agente, ambiente, workspace ativo, limites e proteções. Não lê arquivos do projeto.",
        "inputSchema": {"type": "object", "properties": {}},
        "annotations": {"readOnlyHint": true, "destructiveHint": false, "openWorldHint": false}
      },
      {
        "name": "orbita_set_workspace_root",
        "title": "Definir pasta de trabalho",
        "description": "Define a pasta de projeto que o ORBITA pode acessar...",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string", "minLength": 3, "maxLength": 1024}}},
        "annotations": {"readOnlyHint": false, "destructiveHint": false, "openWorldHint": false}
      },
      {
        "name": "orbita_list_files",
        "title": "Listar arquivos do projeto",
        "description": "Lista arquivos e diretórios dentro do workspace ORBITA...",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string", "default": "."}, "limit": {"type": "integer", "default": 200}, "maxDepth": {"type": "integer", "default": 4}}},
        "annotations": {"readOnlyHint": true, "destructiveHint": false, "openWorldHint": false}
      },
      {
        "name": "orbita_read_file",
        "title": "Ler arquivo de projeto",
        "description": "Lê um arquivo de texto dentro do workspace...",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string", "minLength": 1, "maxLength": 1024}}},
        "annotations": {"readOnlyHint": true, "destructiveHint": false, "openWorldHint": false}
      },
      {
        "name": "orbita_search_files",
        "title": "Pesquisar texto no projeto",
        "description": "Pesquisa uma expressão textual em arquivos do workspace...",
        "inputSchema": {"type": "object", "properties": {"query": {"type": "string", "minLength": 1, "maxLength": 200}, "maxFiles": {"type": "integer", "default": 500}, "maxResults": {"type": "integer", "default": 50}}},
        "annotations": {"readOnlyHint": true, "destructiveHint": false, "openWorldHint": false}
      },
      {
        "name": "orbita_inspect_project",
        "title": "Inspecionar projeto",
        "description": "Detecta linguagens, frameworks e manifests comuns...",
        "inputSchema": {"type": "object", "properties": {}},
        "annotations": {"readOnlyHint": true, "destructiveHint": false, "openWorldHint": false}
      },
      {
        "name": "orbita_git_status",
        "title": "Consultar estado Git",
        "description": "Executa apenas git status no workspace...",
        "inputSchema": {"type": "object", "properties": {}},
        "annotations": {"readOnlyHint": true, "destructiveHint": false, "openWorldHint": false}
      },
      {
        "name": "orbita_git_diff",
        "title": "Consultar diferenças Git",
        "description": "Mostra diffs unstaged e staged somente de arquivos não sensíveis...",
        "inputSchema": {"type": "object", "properties": {"maxChars": {"type": "integer", "default": 18000, "min": 1000, "max": 30000}}},
        "annotations": {"readOnlyHint": true, "destructiveHint": false, "openWorldHint": false}
      },
      {
        "name": "orbita_prepare_file_change",
        "title": "Preparar alteração de arquivo",
        "description": "Cria uma prévia temporária em memória para um arquivo de texto. Não grava no projeto...",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string", "minLength": 1, "maxLength": 1024}, "content": {"type": "string", "maxLength": 1100000}}},
        "annotations": {"readOnlyHint": false, "destructiveHint": false, "openWorldHint": false}
      },
      {
        "name": "orbita_apply_file_change",
        "title": "Aplicar alteração aprovada",
        "description": "Grava uma alteração preparada. Revalida caminho e hash-base...",
        "inputSchema": {"type": "object", "properties": {"token": {"type": "string", "format": "uuid"}}},
        "annotations": {"readOnlyHint": false, "destructiveHint": true, "openWorldHint": false}
      },
      {
        "name": "orbita_run_project_task",
        "title": "Executar teste ou build autorizado",
        "description": "Executa uma tarefa predefinida do projeto...",
        "inputSchema": {"type": "object", "properties": {"task": {"type": "string", "enum": ["npm-test", "npm-build", "npm-lint", "npm-typecheck", "python-pytest", "dotnet-test", "dotnet-build", "go-test", "cargo-test", "cargo-build"]}}},
        "annotations": {"readOnlyHint": false, "destructiveHint": true, "openWorldHint": true}
      }
    ]
  },
  "jsonrpc": "2.0",
  "id": 3
}
```

### 4.5. Requisição `orbita_status` (id=4)

**Solicitação:**
```json
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"orbita_status"}}
```

**Resposta:**
```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"name\": \"ORBITA\",\n  \"version\": \"0.1.0\",\n  \"runtime\": \"Node.js v26.12.1\",\n  \"platform\": \"win32 x64\",\n  \"workspaceRoot\": \"C:\\\\Users\\\\eric\\\\.orbita\\\\workspace\",\n  \"dataDirectory\": \"C:\\\\Users\\\\eric\\\\AppData\\\\Local\\\\ORBITA\",\n  \"limits\": {\n    \"maxReadBytes\": 524288,\n    \"maxWriteBytes\": 1048576,\n    \"maxSearchFiles\": 1500,\n    \"commandTimeoutMs\": 120000\n  },\n  \"protections\": [\n    \"Workspace único e caminhos relativos nas ferramentas de arquivo\",\n    \"Bloqueio de .env, chaves privadas, tokens, credenciais e pastas sensíveis\",\n    \"Links simbólicos para fora do workspace bloqueados\",\n    \"Sem ferramenta de shell arbitrário ou exclusão de arquivos\",\n    \"Alterações passam por prévia, hash-base e gravação atômica\",\n    \"Execução de tarefas predefinidas sujeita à aprovação do host MCP\",\n    \"Auditoria não registra conteúdo dos arquivos nem variáveis de ambiente\"\n  ]\n}"
      }
    ]
  },
  "jsonrpc": "2.0",
  "id": 4
}
```

---

## 5. Resultado Individual de Cada Teste

| # | Teste | Requisição | Resposta | Status |
|---|---|---|---|---|
| 1 | Inicialização STDIO | `node src/index.mjs` | `[ORBITA] Servidor MCP iniciado. Workspace: ...` | ✅ **Aprovado** |
| 2 | Request `initialize` | `{"id":1,"method":"initialize"}` | `{"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{"listChanged":true}},"serverInfo":{"name":"orbita-local","version":"0.1.0"}}}` | ✅ **Aprovado** |
| 3 | Notification `initialized` | `{"id":2,"method":"notifications/initialized"}` | `{"error":{"code":-32601,"message":"Method not found"}}` | ⚠️ **Limitado** — o SDK não trata como notificação |
| 4 | Request `tools/list` | `{"id":3,"method":"tools/list"}` | `11 ferramentas` retornadas com metadados | ✅ **Aprovado** |
| 5 | Quantidade de ferramentas | — | Exatamente **11** (orbita_status, orbita_set_workspace_root, orbita_list_files, orbita_read_file, orbita_search_files, orbita_inspect_project, orbita_git_status, orbita_git_diff, orbita_prepare_file_change, orbita_apply_file_change, orbita_run_project_task) | ✅ **Aprovado** |
| 6 | Escanho de metadados | — | Nome, title, description, inputSchema, annotations de cada ferramenta | ✅ **Aprovado** |
| 7 | Request `orbita_status` | `{"id":4,"method":"tools/call","params":{"name":"orbita_status"}}` | `{"name":"ORBITA","version":"0.1.0","runtime":"Node.js v26.12.1","workspaceRoot":"C:\\Users\\eric\\.orbita\\workspace","dataDirectory":"C:\\Users\\eric\\AppData\\Local\\ORBITA",...}` | ✅ **Aprovado** |
| 8 | STDOUT reservado ao protocolo | — | Todas as linhas são JSON-RPC (`{` no início) | ✅ **Aprovado** |
| 9 | Erros do protocolo | — | `{"jsonrpc":"2.0","id":2,"error":{"code":-32601,"message":"Method not found"}}` | ✅ **Aprovado** (erro formatado corretamente) |
| 10 | Mensagens de diagnóstico | — | Nenhuma saída de diagnóstico em STDOUT | ✅ **Aprovado** |

---

## 6. Análise de Metadados das 11 Ferramentas

| Nº | Ferramenta | `readOnlyHint` | `destructiveHint` | `openWorldHint` |
|---|---|---|---|---|
| 1 | `orbita_status` | `true` | `false` | `false` |
| 2 | `orbita_set_workspace_root` | `false` | `false` | `false` |
| 3 | `orbita_list_files` | `true` | `false` | `false` |
| 4 | `orbita_read_file` | `true` | `false` | `false` |
| 5 | `orbita_search_files` | `true` | `false` | `false` |
| 6 | `orbita_inspect_project` | `true` | `false` | `false` |
| 7 | `orbita_git_status` | `true` | `false` | `false` |
| 8 | `orbita_git_diff` | `true` | `false` | `false` |
| 9 | `orbita_prepare_file_change` | `false` | `false` | `false` |
| 10 | `orbita_apply_file_change` | `false` | `true` | `false` |
| 11 | `orbita_run_project_task` | `false` | `true` | `true` |

**Observações:**

- `orbita_set_workspace_root`: `destructiveHint: false` no código, mas altera o estado do workspace. Requer política explícita de aprovação.
- `orbita_prepare_file_change`: `destructiveHint: false`, mas é apenas uma prévia. A gravação real está em `orbita_apply_file_change` (`destructiveHint: true`).
- `orbita_run_project_task`: `openWorldHint: true` — pode executar código do projeto. Requer aprovação explícita.

---

## 7. Erros e Limitacões

| Erro / Limitação | Impacto | Mitigação |
|---|---|---|
| `notifications/initialized` retorna "Method not found" | O host pode registrar erro na interface do cliente | Host deve ignorar erros de notificações não implementadas |
| `destructiveHint: false` em `orbita_set_workspace_root` | Host pode não pedir confirmação de segurança | Política de aprovação explícita do agente |
| `destructiveHint: false` em `orbita_prepare_file_change` | Host pode não mostrar aviso de risco | Documentar que a prévia não grava |
| STDIO não permite conexão remota | O plugin só funciona em hosts desktop que lançam subprocessos | Limitação de arquitetura |

---

## 8. Conclusão

O servidor MCP STDIO do ORBITA está **funcional**:

- ✅ Inicialização correta (`node src/index.mjs` inicia e aguarda input)
- ✅ `initialize` retorna protocolVersion 2024-11-05 e serverInfo `orbita-local@0.1.0`
- ✅ `tools/list` retorna exatamente 11 ferramentas com schemas e annotations válidos
- ✅ `orbita_status` retorna o objeto de status completo
- ✅ STDOUT é reservado ao protocolo (todas as saídas são JSON-RPC)
- ⚠️ `notifications/initialized` não é tratada como notificação pelo SDK — o host deve ignorar o erro

**Verdict: PARCIAL** — O servidor MCP está operacional e o protocolo está correto. A validação de conexão com ChatGPT exige execução no host (não contemplada nesta fase).

**Próximos passos:**
1. Executar no ChatGPT Desktop/Codex para confirmar descoberta de 11 ferramentas
2. Testar `orbita_set_workspace_root` com aprovação explícita
3. Testar prévia + aplicação de arquivo
4. Confirmar que `notifications/initialized` não causa falha no host
