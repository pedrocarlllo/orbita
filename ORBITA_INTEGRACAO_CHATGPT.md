# ORBITA_INTEGRACAO_CHATGPT.md

**Versão da especificação:** 0.1.0  
**Projeto base:** `C:/ORBITA-Universal-Plugin-Windows-0.1.0/orbita-agent`  
**Última reunião:** 31/10/2026  
**Estado:** Especificação de integração a ser validada contra o host (STDIO transport)  
**Referências:** `ORBITA_ESPECIFICACAO_COMPLETA_PLUGIN_CHATGPT.md` (arquitetura original), `server/src/tools.mjs` (contratos reais), `README.md` (instalação), `docs/technical-spec.md` (design).

---

## 0. Princípio de projeto

O ORBITA 0.1.0 permanece inalterado. A integração com o ChatGPT é construída **ao redor** do servidor MCP existente:

1. O servidor MCP (`orbita-agent/server/src/index.mjs`) continua sendo a fonte de verdade dos contratos.
2. Os manifestos de integração (`.mcp.json`, `plugin.json`, `.codex-plugin/plugin.json`) são alinhados.
3. A camada de instruções (skills) orienta o agente a usar as ferramentas corretamente.
4. A validação final é feita no host real (ChatGPT Desktop/Codex), não apenas no código.

**Regra de liberação:** só se pode afirmar "funciona no ChatGPT" depois de comprovar que o host inicia o processo STDIO e recebe 11 ferramentas. O código sozinho não comprova isso.

---

## 1. Compatibilidade de transporte

### 1.1. Modalidade escolhida: STDIO (local)

| Item | Valor |
|---|---|
| Transporte | `stdio` (STDIO JSON-RPC) |
| Inicialização | Host lança `node orbita-agent/server/src/index.mjs` |
| Diretório de trabalho | `server/` (definido em `.mcp.json`) |
| Autenticação | Não aplicável (localhost) |
| Rede | Não usada |
| Retorno de chamada | `initialize`, `tools/list`, `tools/call`, `notifications/initialized` |
| Requisito do host | Clientes desktop em modo sandbox que podem lançar processos locale |

### 1.2. Por que STDIO só para hosts desktop

O STDIO é um canal local: o host lança um processo e comunica via `stdin`/`stdout`. O ChatGPT Web e o acesso via celular não possuem a mesma capacidade de lançar subprocessos locais de forma segura. A compatibilidade com STDIO é garantida em:

- **ChatGPT Desktop** (Windows/macOS/Linux) — via `.mcp.json` ou marketplace.
- **Codex** (Clime) — via `.mcp.json` ou configuração nativa.

**Limitação:** o ChatGPT Web e dispositivos móveis não têm acesso ao filesystem local através do STDIO. O plugin ORBITA só deve ser publicado e usados nesses ambientes.

### 1.3. Verificação de compatibilidade do transporte

Antes de afirmar compatibilidade, executar os passos:

```powershell
# No diretório server/
cd C:/ORBITA-Universal-Plugin-Windows-0.1.0/orbita-agent/server
node src/index.mjs
```

O servidor deve imprimir `[ORBITA] Servidor MCP iniciado. Workspace: <caminho>` e aguardar input STDIO. Saída desse processo comprova que o host consegue iniciar o servidor.

**Nunca afirmar** "já funciona no ChatGPT" antes destes passos.

---

## 2. Manifestos — Funções e conflitos

### 2.1. Resumo dos manifestos

| Arquivo | Escopo | Host | Papel |
|---|---|---|---|
| `plugin.json` | Manifesto portable Agent Plugins 1.0 | ChatGPT Desktop, Codex compatível | Define nome, versão, descrição, extensões |
| `.mcp.json` | Configuração MCP do plugin nativo | ChatGPT Desktop | Liga o servidor MCP via STDIO |
| `.codex-plugin/plugin.json` | Manifesto nativo do Codex | Codex | Variantes da interface (`interface` object) |
| `mcp.json` | Servidor MCP standalone | Hospedeiros MCP | Configuração de servidor (não é plugin) |

### 2.2. Estrutura do `.mcp.json` (arquivo de configuração MCP)

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "orbita-local": {
      "type": "stdio",
      "command": "node",
      "args": ["${PLUGIN_ROOT}/orbita-agent/server/src/index.mjs"],
      "cwd": "${PLUGIN_ROOT}/orbita-agent/server"
    }
  }
}
```

**Pontos de atenção:**

- `${PLUGIN_ROOT}` é expandido pelo host MCP, **não** pelo shell. O bash não deve expandir.
- `type: "stdio"` é obrigatório no esquema do agent-plugins.org.
- O argumento aponta para `orbita-agent/server/src/index.mjs` — o entry point no layout deste repositório.

### 2.3. Estrutura de `plugin.json`

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "orbita-agent",
  "version": "0.1.0",
  "description": "Agente universal local independente de projetos, com acesso controlado à pasta que o usuário selecionar.",
  "author": { "name": "ORBITA Project" },
  "keywords": ["universal-agent", "mcp", "local-agent", "windows", "project-tools", "software-engineering"],
  "extensions": {
    "com.openai": {
      "interface": {
        "displayName": "ORBITA",
        "shortDescription": "Agente universal local",
        "longDescription": "Agente universal local para ChatGPT Desktop/Codex. Instalado fora dos projetos. Permite alternar entre projetos por caminho absoluto, com ferramentas locais MCP e controles de segurança.",
        "developerName": "ORBITA Project",
        "category": "Developer Tools",
        "capabilities": ["Read", "Write", "Interactive"],
        "defaultPrompt": [
          "ORBITA, aguarde eu indicar o caminho do projeto e depois faça uma análise completa.",
          "ORBITA, troque para a pasta de projeto que eu indicar e investigue este problema.",
          "ORBITA, analise o projeto selecionado e proponha alterações com evidências."
        ],
        "brandColor": "#2563EB"
      }
    }
  }
}
```

### 2.4. Estrutura de `.codex-plugin/plugin.json`

```json
{
  "name": "orbita-agent",
  "version": "0.1.0",
  "description": "Agente universal local independente de projetos, com acesso controlado à pasta selecionada pelo usuário.",
  "author": { "name": "ORBITA Project" },
  "homepage": "https://learn.chatgpt.com/docs/extend/mcp",
  "license": "MIT",
  "keywords": ["programming", "software-engineering", "mcp", "local-agent", "windows", "project-analysis"],
  "skills": "./skills/",
  "mcpServers": "./.mcp.json",
  "interface": {
    "displayName": "ORBITA",
    "shortDescription": "Agente universal local",
    "longDescription": "Plugin universal instalado fora dos projetos. Permite selecionar e alternar entre pastas de projeto por caminho absoluto, com ferramentas locais MCP e controles de segurança.",
    "developerName": "ORBITA Project",
    "category": "Developer Tools",
    "capabilities": ["Read", "Write", "Interactive"],
    "defaultPrompt": [
      "ORBITA, aguarde eu indicar o caminho do projeto e depois faça uma análise completa.",
      "Investigue este erro, identifique a causa provável e proponha uma correção verificável.",
      "Prepare uma alteração de código, mostre a prévia e aguarde minha aprovação."
    ],
    "brandColor": "#2563EB"
  }
}
```

### 2.5. Resumo de responsabilidades

```
Host MCP (ChatGPT Desktop / Codex)
  ├── Lê plugin.json → exibe ORBITA no marketplace
  ├── Lê .mcp.json → inicia o servidor (node + index.mjs)
  └── Envia solicitações tools/call → ORBITA MCP Server (STDIO)
        ├── tools/list → 11 ferramentas (index.mjs)
        ├── tools/call → executa a ferramenta
        └── notif/init → servidor confirma início
```

---

## 3. Comunicação — Inicialização e descoberta

### 3.1. Fluxo de inicialização

```
1. Host (ChatGPT Desktop) lê .mcp.json
2. Host lança: node orbita-agent/server/src/index.mjs  (cwd = orbita-agent/server/)
3. Server inicia McpServer, registra 11 ferramentas
4. Server informa mudança de workspace (state)
5. Server dispara notif/init → Host confirma
6. Host responde requests/tools/list → 11 ferramentas
7. Host pode enviar tools/call para qualquer ferramenta
```

### 3.2. Descoberta das 11 ferramentas

O servidor não expõe um array atômico de nomes. Em vez disso, usa o padrão:

```
index: 0..10  (count = 11)
```

O `index.mjs` resolve ferramentas pelo prefixo `orbita_` + `index`/`count`, com mapa de ferramentas disponíveis. O host (ChatGPT) enumere chamando `tools/list` e receberá os 11 nomes:

| Nº | Nome da ferramenta |
|---|---|
| 1 | `orbita_status` |
| 2 | `orbita_set_workspace_root` |
| 3 | `orbita_list_files` |
| 4 | `orbita_read_file` |
| 5 | `orbita_search_files` |
| 6 | `orbita_inspect_project` |
| 7 | `orbita_git_status` |
| 8 | `orbita_git_diff` |
| 9 | `orbita_prepare_file_change` |
| 10 | `orbita_apply_file_change` |
| 11 | `orbita_run_project_task` |

### 3.3. Protocolo JSON-RPC essencial

| MENSAGEM | SEQ | PARAMETROS | RETORNO |
|---|---|---|---|
| `initialize` | Host → Server | `protocolVersion`, `capabilities`, `clientInfo` | `protocolVersion`, `capabilities`, `serverInfo`, `meta` |
| `notifications/initialized` | Host → Server | nenhum | `null` |
| `tools/list` | Host → Server | nenhum | `tools: [{name, title, description, inputSchema, annotations}]` |
| `tools/call` | Host → Server | `name`, `arguments` (opcional) | `{content: [{type: "text", text}], isError?}` |
| `initialized` | Server → Host | nenhum | `null` (notif) |

---

## 4. Segurança — Aprovações, permissões, prévias, gravações

### 4.1. Políticas de aprovação por ferramenta

| Ferramenta | `readOnlyHint` | `destructiveHint` | `openWorldHint` | Política de aprovação recomendada |
|---|---|---|---|---|
| `orbita_status` | true | false | false | nenhuma |
| `orbita_set_workspace_root` | false | false | false | **AVISO DE SEGURANÇA** — altera workspace ativo; modal de confirmação do host recomendado |
| `orbita_list_files` | true | false | false | nenhuma |
| `orbita_read_file` | true | false | false | nenhuma |
| `orbita_search_files` | true | false | false | nenhuma |
| `orbita_inspect_project` | true | false | false | nenhuma |
| `orbita_git_status` | true | false | false | nenhuma |
| `orbita_git_diff` | true | false | false | nenhuma |
| `orbita_prepare_file_change` | false | false | false | prévia — sem gravação; mostrar resumo e aguardar aprovação |
| `orbita_apply_file_change` | false | true | false | **GERAR APROVAÇÃO DO HOST** — gravação real; não usar autoaprovação |
| `orbita_run_project_task` | false | true | true | **GERAR APROVAÇÃO DO HOST** — executa código do projeto; modal explícito |

### 4.2. Regra para `orbita_set_workspace_root`

Embora o código use `destructiveHint: false` (como não há perda de dados), a operação **altera o workspace ativo**, o que pode surpreender o usuário. Recomenda-se a seguinte política:

- **Sem aprovação explícita do usuário:** o agente pode chamar, mas deve avisar que o workspace mudou.
- **Com aprovação do host:** o agente deve pedir confirmação antes de chamar a ferramenta.
- **Validação:** o valor deve ser um caminho absoluto, existente e dentro de uma unidade. Contraste com raiz de unidade.

### 4.3. Fluxo de preparação e gravação

```
1. orbita_prepare_file_change(path, content)
   → Retorna: token (UUID), diffs, sha256_before, sha256_after, expiresIn 300s
   → Não grava no disco

2. (Aguardar aprovação do usuário)

3. orbita_apply_file_change(token)
   → Confere sha256_before (concorrente)
   → Cria backup (dataDir/backups/)
   → Grava temp + rename (atomic)
   → Retorna: sha256_after, bytesWritten, backupPath
```

### 4.4. Fluxo de execução de tarefas

```
1. orbita_run_project_task(task)
   → Valida que task está no enum fechado
   → Verifica que projetos detectados suportam a linguagem
   → Executa comando definido (npm, pytest, dotnet, go, cargo)
   → Timeout e limite de saída aplicados
   → Retorna: exitCode, success, durationMs, stdout, stderr
```

### 4.5. Limites

| Recurso | Limite |
|---|---|
| Bytes lidos por ferramenta de leitura | `maxReadBytes` (config) |
| Bytes escritos por ferramenta de alteração | `maxWriteBytes` (config) |
| Busca em arquivos | `maxSearchFiles` (config) |
| Timeout de tarefa | `commandTimeoutMs` (config, default 60s) |
| Expiração de token de prévia | 5 minutos (300s) |
| Ajuda de saída | Limite de 28.000 caracteres por chamada |
| Arquivos lidos em busca | `maxFiles` (config, default 500) |
| Resultados de busca | `maxResults` (config, default 50) |

---

## 5. Experiência do agente — Instruções para o ChatGPT

### 5.1. Princípios de uso

1. **Primeiro, descubra o workspace ativo** via `orbita_status` ou `orbita_list_files`.
2. **Antes de alterar**, use `orbita_prepare_file_change` e mostre a prévia ao usuário.
3. **Só depois de aprovação**, use `orbita_apply_file_change` com o token.
4. **Pergunte antes de executar** `orbita_run_project_task`.
5. **Use somente ferramentas disponíveis**; o host não expõe ferramentas inexistentes.

### 5.2. Fluxo orientacional

```
1. Usuário diz: "trabalhe em C:\Projeto\Atual"
2. Agent pega orbita_set_workspace_root com o caminho
3. Fecha: ORBITA, workspace definido como C:\Projeto\Atual
4. Usuário diz: "analise o projeto"
5. Agent chama orbita_inspect_project → recebe linguagens, manifests, scripts
6. Usuário diz: "mostre os arquivos principais"
7. Agent chama orbita_list_files (limite 50, profundidade 3)
8. Usuário diz: "encontre todos os erros no código"
9. Agent chama orbita_search_files(query="error|bug|fix", maxFiles=200, maxResults=50)
10. Usuário diz: "prepare a correção no arquivo X"
11. Agent chama orbita_prepare_file_change → mostra prévia
12. Usuário aprova → Agent chama orbita_apply_file_change(token)
13. Usuário diz: "execute os testes"
14. Agent pergunta: "Deseja executar npm test? Isso executará o script de teste do projeto."
15. Usuário concorda → Agent chama orbita_run_project_task("npm-test")
```

### 5.3. Exemplo de prompt para o ChatGPT

```text
ORBITA, aguarde eu indicar o caminho do projeto e depois faça uma análise completa.
Depois, prepare um relatório estruturado com: tecnologias detectadas, arquivos principais,
testes existentes, e possíveis melhorias.

Se algo precisar ser alterado, mostre a prévia primeiro e aguarde minha aprovação.
Se precisar executar testes, pergunte antes e não execute sem confirmação.
```

---

## 6. Instalação e configuração

### 6.1. Pré-requisitos

- Node.js 22 LTS ou superior
- Windows 10/11 (para variáveis de ambiente `${PLUGIN_ROOT}`)
- ChatGPT Desktop ou Codex compatível (não funciona no Web)

### 6.2. Passo a passo

```powershell
# 1. Extraia o ZIP para um diretório temporário
# 2. Abra PowerShell nesse diretório
powershell -NoProfile -ExecutionPolicy Bypass -File .\.scripts\Install-ORBITA.ps1
# 3. Server copia para %USERPROFILE%\plugins\orbita-agent,
#    instala dependências e registra no marketplace
# 4. Reinicie ChatGPT Desktop
# 5. Vá em "Plugins" → "Adicionar plugin" → "A partir de arquivo"
# 6. Selecione .mcp.json (ou use o marketplace)
# 7. Verifique o servidor MCP em Settings → MCP Servers
# 8. Invocar: ORBITA, status → Deve confirmar 11 ferramentas disponíveis
```

### 6.2.1. Instalação via `Install-ORBITA.ps1`

O script executa:

1. Copia a pasta `orbita-agent` para `%USERPROFILE%\plugins\orbita-agent`.
2. Executa `npm install` no diretório `server/`.
3. Registra o plugin no marketplace (`%USERPROFILE%\.agents\plugins\marketplace.json`) com:
   - `name: "orbita-agent"`
   - `mcpServers: { "orbita-local": { type: "stdio", command: "node", args: ["${PLUGIN_ROOT}/orbita-agent/server/src/index.mjs"], cwd: "${PLUGIN_ROOT}/orbita-agent/server" } }`

### 6.3. Desinstalação

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\.scripts\Uninstall-ORBITA.ps1
```

O script remove o registro do marketplace e a pasta `%USERPROFILE%\plugins\orbita-agent`.

### 6.4. Variáveis de ambiente

| Variável | Uso | Exemplo |
|---|---|---|
| `PLUGIN_ROOT` | Substituído pelo host MCP para o diretório do plugin | `C:\Users\eric\plugins\orbita-agent` |
| `ORBITA_DATA_DIR` | Pasta de dados do ORBITA (%LOCALAPPDATA%\ORBITA) | `C:\Users\eric\AppData\Local\ORBITA` |

### 6.5. Arquivos de configuração

| Arquivo | Local | Conteúdo |
|---|---|---|
| `.mcp.json` | Raiz do plugin | Configuração MCP (STDIO) |
| `plugin.json` | Raiz do plugin | Manifesto portable |
| `.codex-plugin/plugin.json` | Raiz do plugin | Manifesto nativo do Codex |
| `server/package.json` | `server/` | Dependências do servidor |
| `orbita-agent/server/src/index.mjs` | `orbita-agent/server/src/` | Entry point do servidor |
| `server/src/tools.mjs` | `server/src/` | 11 ferramentas implementadas |
| `server/src/security.mjs` | `server/src/` | Guardas de segurança |
| `server/src/state.mjs` | `server/src/` | Estado e workspace |
| `server/src/approvals.mjs` | `server/src/` | Gestão de tokens de prévia |
| `server/src/audit.mjs` | `server/src/` | Log de auditoria |
| `server/src/workspace.mjs` | `server/src/` | Acesso aos arquivos |
| `server/src/process.mjs` | `server/src/` | Execução de processos |

---

## 7. Validação — O que comprovar antes de distribuição

### 7.1. Checklist de validação

| Etapa | Comando | Esperado | Status |
|---|---|---|---|
| 1. Inicialização | `cd server && node src/index.mjs` | Saída STDIO, aguarda input | ✅ / ❌ |
| 2. Descoberta de ferramentas | Host lê `tools/list` | 11 ferramentas listadas | ✅ / ❌ |
| 3. Leitura fora do workspace | Host chama `orbita_read_file` com `../../etc/passwd` | Recusado | ✅ / ❌ |
| 4. Leitura de segredos | Host chama `orbita_read_file` com `.env` | Recusado | ✅ / ❌ |
| 5. Prévia + aplicação | `orbita_prepare_file_change` → `orbita_apply_file_change` | Arquivo salvo, hash verificado | ✅ / ❌ |
| 6. Execução de tarefa | `orbita_run_project_task` | Retorna exit code e stdout | ✅ / ❌ |
| 7. Listagem de arquivos | `orbita_list_files` | Lista correta | ✅ / ❌ |

### 7.2. Padrões de aprovação

| Modo | Uso recomendado |
|---|---|
| `never` | Nenhum comando de escrita |
| `prompt` | Pede confirmação para cada operação |
| `writes` | Apenas operações de escrita pedem aprovação |
| `yes` | Autoaprovação (não recomendado para `apply_file_change` e `run_project_task`) |

**Recomendação:** use `writes` no modo de aprovação do host para `orbita_apply_file_change`, `orbita_run_project_task` e `orbita_set_workspace_root`.

### 7.3. Limitações conhecidas

A integração STDIO com ChatGPT Desktop/Codex tem limitações reais:

1. **Acesso local:** o plugin só funciona em ambientes desktop que lançam subprocessos.
2. **Segurança do sandbox:** o host utiliza o sandbox Windows para conter o acesso ao filesystem.
3. **Sobreposição de permissões:** a segurança do ORBITA é adicional ao sandbox do host; não substitui o sandbox.
4. **Politica de aprovação:** as políticas de aprovação do ChatGPT são aplicadas pelo host e não pelo servidor.

---

## 8. Armazenamento de estado e persistência

### 8.1. Caminhos de dados

| Recurso | Local do Windows |
|---|---|
| Configuração | `%LOCALAPPDATA%\ORBITA\config.json` |
| Workspace inicial | `%LOCALAPPDATA%\ORBITA\workspace` |
| Backups | `%LOCALAPPDATA%\ORBITA\backups\` |
| Auditoria | `%LOCALAPPDATA%\ORBITA\audit.jsonl` |
| Plugins | `%USERPROFILE%\plugins\orbita-agent` |
| Marketplace | `%USERPROFILE%\.agents\plugins\marketplace.json` |

### 8.2. Dados do servidor

| Recurso | Local | Descrição |
|---|---|---|
| `dataDir` | `%LOCALAPPDATA%\ORBITA` | Pasta raiz de dados |
| `workspaceRoot` | config/user | Pasta ativa do projeto |
| `audit` | `dataDir/audit.jsonl` | Registro JSONL de ações |
| `approvals` | memória do processo | Tokens de prévia, expiram em 5min |
| `config` | `dataDir/config.json` | Limites e configurações |

---

## 9. Glossário rápido

| Termo | Significado |
|---|---|
| `STDIO` | Transporte de comunicação via stdin/stdout (JSON-RPC) |
| `MCP server` | Módulo que expõe ferramentas via MCP STDIO |
| `Plugin` | Arquivo de manifesto (`plugin.json`) que o host lê |
| `Manifesto MCP` | Arquivos `.mcp.json` que registram o servidor |
| `Tools` | Funções expostas pelo servidor MCP |
| `Sandbox` | Isolamento do host (Windows sandbox / AppContainer) |
| `Approval policy` | Regra que o host impõe antes de cada ferramenta |
| `Pre-view` | Opera `orbita_prepare_file_change` (nem grava) |
| `Apply` | Opera `orbita_apply_file_change` (grava de verdade) |
| `Open world` | Ferramenta que pode acessar qualquer recurso do host |
| `Read-only` | Ferramenta que só lê recursos |
| `Write` | Ferramenta que grava ou altera recursos |
| `Destructive` | Ferramenta potencialmente destrutiva (ex: grava arquivos, executa código) |

---

*Documento gerado em 31/10/2026. Base: ORBITA 0.1.0, servidor MCP STDIO. Validação no host necessária a partir deste ponto.*
