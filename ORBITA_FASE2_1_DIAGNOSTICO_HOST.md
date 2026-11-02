# ORBITA_FASE2_1_DIAGNOSTICO_HOST.md

**Versão do diagnóstico:** 0.1.0  
**Data:** 31/10/2026  
**Objetivo:** Verificar se o ORBITA está configurado corretamente para ser iniciado por um host MCP real (ChatGPT Desktop ou Codex).  

**Regra aplicada:** Não modificar arquivos. Servidor validado em STDIO independente; não se presume conexão com o host.

---

## 1. Host identificado

| Item | Valor |
|---|---|
| Host ativo | **Não verificável neste ambiente** |
| Especificação | Sandbox de execução de agente (sem acesso ao ChatGPT Desktop ou Codex) |
| Versão do host | **Não disponível** — não houve acesso ao processo do host |
| Mecanismo de descoberta de servidores MCP | **Não conhecido** — não há acesso ao host |
| Local de configuração MCP | **Não verificável** — não há acesso ao host |
| Suporte a transporte STDIO | **Possível** — acessível via Node.js (ver `server/src/index.mjs`) |

### Observação crítica

O ORBITA não pode ser afirmado como integrado ao ChatGPT Desktop ou Codex apenas com testes STDIO no ambiente de desenvolvimento. A conexão real só pode ser verificada executando o host e consultando seu estado MCP.

---

## 2. Configuração encontrada

### 2.1 `.mcp.json`

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
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

| Campo | Valor | Observação |
|---|---|---|
| Schema | `https://agent-plugins.org/schemas/1.0.0/mcp.schema.json` | ✅ |
| Type | `stdio` | ✅ Suporte a transporte STDIO |
| Command | `node` | ✅ Executável disponível no ambiente |
| Args | `${PLUGIN_ROOT}/server/src/index.mjs` | ✅ Ponto de entrada do servidor |
| CWD | `${PLUGIN_ROOT}/server` | ✅ Diretório de trabalho do servidor |

### 2.2 `mcp.json` (versionado)

O mesmo conteúdo de `.mcp.json`. Ambos são válidos.

### 2.3 `plugin.json`

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "orbita-agent",
  "version": "0.1.0",
  "description": "Agente local universal independente de projetos, com acesso controlado à pasta que o usuário selecionar.",
  "extensions": {
    "com.openai": {
      "interface": {
        "displayName": "ORBITA",
        "capabilities": ["Read", "Write", "Interactive"],
        "brandColor": "#2563EB"
      }
    }
  }
}
```

| Campo | Valor |
|---|---|
| name | `orbita-agent` |
| version | `0.1.0` |
| displayName | `ORBITA` |
| capabilities | `Read`, `Write`, `Interactive` |
| Extension | `com.openai` (ChatGPT Desktop) |

### 2.4 `.codex-plugin/plugin.json`

```json
{
  "name": "orbita-agent",
  "version": "0.1.0",
  "mcpServers": "./.mcp.json",
  "interface": {
    "displayName": "ORBITA",
    "capabilities": ["Read", "Write", "Interactive"]
  }
}
```

| Campo | Valor |
|---|---|
| name | `orbita-agent` |
| mcpServers | `./.mcp.json` (referência ao configuração MCP) |
| interface | `ORBITA` com capabilities Read/Write/Interactive |

---

## 3. Estado da conexão com o host

| Verificação | Resultado |
|---|---|
| Host acessível? | ❌ **Não verificável** — não há acesso ao ChatGPT Desktop/Codex |
| Servidor ORBITA na lista de MCP? | ❌ Não possível consultar |
| Estado do servidor (conectado/desconectado/erro)? | ❌ Não possível consultar |
| Host consegue iniciar o processo? | ⚠️ Candidato, mas não confirmado no host |
| Mensagens de erro no host? | ❌ Não verificáveis sem acesso |
| Host consegue realizar chamada MCP? | ❌ Não verificável |

### Declaração formal

> **A conexão com o host MCP não pôde ser verificada porque o ambiente atual não possui acesso ao ChatGPT Desktop ou Codex.** Os arquivos de configuração foram inspecionados e validados, mas o estado da conexão só pode ser confirmado executando o host.

---

## 4. Descoberta de ferramentas

| Verificação | Resultado |
|---|---|
| Host com conexão ativa? | ❌ Não verificável |
| `tools/list` pelo host? | ❌ Não executado (sem conexão) |
| Total de ferramentas descobertas? | ❌ Não verificável |

### Verificação via código (`server/src/tools.mjs`)

O arquivo `server/src/tools.mjs` registra exatamente **11 ferramentas** via `registerOrbitaTools()`:

| Nº | Ferramenta | Title |
|---|---|---|
| 1 | `orbita_status` | Status do ORBITA |
| 2 | `orbita_set_workspace_root` | Definir pasta de trabalho |
| 3 | `orbita_list_files` | Listar arquivos do projeto |
| 4 | `orbita_read_file` | Ler arquivo de projeto |
| 5 | `orbita_search_files` | Pesquisar texto no projeto |
| 6 | `orbita_inspect_project` | Inspecionar projeto |
| 7 | `orbita_git_status` | Consultar estado Git |
| 8 | `orbita_git_diff` | Consultar diferenças Git |
| 9 | `orbita_prepare_file_change` | Preparar alteração de arquivo |
| 10 | `orbita_apply_file_change` | Aplicar alteração aprovada |
| 11 | `orbita_run_project_task` | Executar teste ou build autorizado |

### Comparação entre código e especificação

| Fonte | Contagem | Nomes |
|---|---|---|
| `server/src/tools.mjs` | **11** | `orbita_status`, `orbita_set_workspace_root`, `orbita_list_files`, `orbita_read_file`, `orbita_search_files`, `orbita_inspect_project`, `orbita_git_status`, `orbita_git_diff`, `orbita_prepare_file_change`, `orbita_apply_file_change`, `orbita_run_project_task` |
| Especificação | **11** | Mesmo conjunto |

**Conclusão:** O código registra 11 ferramentas MCP. Para confirmar que o host descobre exatamente essas 11, é necessário executar o host e consultar `tools/list`.

---

## 5. Arquivos inspecionados

| Arquivo | Status | Observação |
|---|---|---|
| `.mcp.json` | ✅ Inspecionado | Configuração STDIO válida |
| `mcp.json` | ✅ Inspecionado | Idêntico a `.mcp.json` |
| `plugin.json` | ✅ Inspecionado | Manifesto portable |
| `.codex-plugin/plugin.json` | ✅ Inspecionado | Manifesto nativo do Codex |
| `server/src/index.mjs` | ✅ Inspecionado | Entry point; `serveStdio(createServer)` |
| `server/src/tools.mjs` | ✅ Inspecionado | 11 ferramentas registradas |
| `README.md` | ✅ Inspecionado | Guia de instalação |

---

## 6. Problemas identificados

| Problema | Severidade | Solução |
|---|---|---|
| Host não acessível | Alta | Verificar acesso ao ChatGPT Desktop/Codex |
| `notifications/initialized` mal tratada pelo SDK | Média | Corrigir script de teste a chamar sem `id` (já feito em OT-17) |
| `destructiveHint: false` em `orbita_set_workspace_root` | Baixa | Adicionar política explícita de aprovação no host |
| `destructiveHint: false` em `orbita_prepare_file_change` | Baixa | Documentar que é prévia, não gravação |
| `orbita_run_project_task` permite `openWorldHint: true` | Média | Manter aprovação explícita do host |

---

## 7. Diferenciação de encerramento (validação adicional)

| Cenário | Comportamento esperado |
|---|---|
| **Encerramento gracioso** | Fechar STDIN com EOF → servidor termina naturalmente |
| **Encerramento forçado** | `proc.kill()` → processo terminado imediatamente |

No relatório OT-17, o script de validação `validate_fc2.py` termina com `proc.kill()`, o que significa que **apenas o encerramento forçado foi comprovado**. A validação do encerramento gracioso requer:
1. Encurtamento do servidor (fecha STDIN)
2. Aguarda por `proc.wait(timeout=5)`
3. Verificar se o processo saiu sozinho (código de saída 0) ou se foi forçado (código diferente)

Este teste adicional não foi executado nesta fase.

---

## 8. Veredito

| Critério | Status |
|---|---|
| Host inicia o servidor | ⚠️ Indeterminado (sem acesso ao host) |
| Host descobre 11 ferramentas | ⚠️ Indeterminado (sem acesso ao host) |
| Configuração válida | ✅ **APROVADA** (arquivos inspecionados, sintaxe validada, comando confirmado) |
| Conexão MCP | ❌ **NÃO VERIFICADA** (falta acesso ao host) |

**Verdict: PARCIAL**

Configuração de integração identificada e válida. Conexão real com o ChatGPT Desktop ou Codex não pôde ser confirmada porque o ambiente de execução não possui acesso ao host MCP.

---

## 9. Próximos passos recomendados

1. **Executar o host MCP** (ChatGPT Desktop ou Codex) com o plugin de ORBITA instalado.
2. **Verificar o estado** do servidor no host (Settings → MCP servers ou `/mcp`).
3. **Listar as ferramentas** disponíveis no host e comparar com o inventário de `server/src/tools.mjs`.
4. **Executar `orbita_status`** pelo host e confirmar resposta.
5. **Testar operações de escrita** com aprovação explícita do usuário.

---

*Relatório gerado em 31/10/2026.*  
*ORBITA Fase 2.1 — Diagnóstico de integração com host MCP.*  
*Preparatório para a fase 2.2 — Validação da conexão real.*
