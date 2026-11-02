# ORBITA — DIAGNÓSTICO TÉCNICO INICIAL (FASE 0)

**Versão do diagnóstico:** 0.1.0
**Data:** 31/10/2026
**Projeto:** ORBITA Universal Plugin Windows 0.1.0
**Diretório do projeto:** `C:/ORBITA-Universal-Plugin-Windows-0.1.0/orbita-agent`
**Node.js:** v26.12.1
**npm:** 11.20.0

---

## 1. OBJETIVO

Executar o Diagnóstico Completo do Projeto Existente, conforme a missão ORBITA WINDOWS SERVER:

1. Inspecionar toda a estrutura do projeto ORBITA.
2. Ler o código-fonte completo.
3. Identificar as 11 ferramentas MCP existentes.
4. Identificar dependências e requisitos.
5. Analisar as proteções de segurança.
6. Identificar funcionalidades incompletas.
7. Gerar um diagnóstico técnico inicial.

## 2. ESTRUTURA DO PROJETO

### 2.1 Diretório raiz

| Item | Status |
|---|---|
| `.gitignore` | ✅ Presente |
| `.mcp.json` | ✅ Presente |
| `mcp.json` | ✅ Presente |
| `plugin.json` | ✅ Presente |
| `.codex-plugin/plugin.json` | ✅ Presente |
| `README.md` | ✅ Presente |
| `docs/` | ✅ Presente |
| `scripts/` | ✅ Presente |
| `server/` | ✅ Presente |
| `skills/` | ✅ Presente |
| `ORBITA_ESPECIFICACAO_COMPLETA_PLUGIN_CHATGPT.md` | ✅ Presente |
| `ORBITA_INTEGRACAO_CHATGPT.md` | ✅ Presente |
| `ORBITA_FASE2_1_DIAGNOSTICO_HOST.md` | ✅ Presente |
| `ORBITA_FASE2_2_INTEGRACAO_CHATGPT_DESKTOP.md` | ✅ Presente |
| `ORBITA_VALIDACAO_MCP_FASE1.md` | ✅ Presente |
| `ORBITA_RETESTE_NOTIFICATIONS.md` | ✅ Presente |
| `ORBITA_CORRECAO_VALIDATE_FC2.md` | ✅ Presente |
| `ot002_report.md` | ✅ Presente |
| `OT006.ps1` / `OT006_CLEAN.ps1` | ✅ Presentes |
| `reteste_notif.sh` | ✅ Presente |

### 2.2 `server/`

| Item | Status |
|---|---|
| `server/package.json` | ✅ Presente |
| `server/package-lock.json` | ✅ Presente |
| `server/node_modules/` | ✅ Presente (deps instaladas) |
| `server/src/` | ✅ Presente |
| `server/test/` | ✅ Presente (3 arquivos) |

### 2.3 `server/src/` (8 arquivos)

| Arquivo | Rôle |
|---|---|
| `index.mjs` | Entry point do servidor MCP |
| `tools.mjs` | Registro de 11 ferramentas MCP |
| `security.mjs` | Guardas de segurança (path traversal, segredos, symlink) |
| `state.mjs` | Estado, configuração e workspace |
| `workspace.mjs` | Acesso aos arquivos, leitura, busca, listagem |
| `process.mjs` | Execução de processos com ambiente seguro |
| `approvals.mjs` | Gestão de tokens de prévia (tokens de uso único) |
| `audit.mjs` | Registro de auditoria JSONL |

### 2.4 `server/test/` (3 arquivos)

| Arquivo | Rôle |
|---|---|
| `security.test.mjs` | Validação de path traversal, caminhos sensíveis, symlink |
| `approvals.test.mjs` | Token de aprovação, SHA-256 |
| `process.test.mjs` | Ambiente seguro exclui chaves de API e NODE_OPTIONS |

## 3. 11 FERRAMENTAS MCP EXISTENTES

O `server/src/tools.mjs` registra exatamente 11 ferramentas MCP:

| # | Ferramenta | Title | Tipo de anotação |
|---|---|---|---|
| 1 | `orbita_status` | Status do ORBITA | readOnly: true |
| 2 | `orbita_set_workspace_root` | Definir pasta de trabalho | readOnly: false, destrutivo: false |
| 3 | `orbita_list_files` | Listar arquivos do projeto | readOnly: true |
| 4 | `orbita_read_file` | Ler arquivo de projeto | readOnly: true |
| 5 | `orbita_search_files` | Pesquisar texto no projeto | readOnly: true |
| 6 | `orbita_inspect_project` | Inspecionar projeto | readOnly: true |
| 7 | `orbita_git_status` | Consultar estado Git | readOnly: true |
| 8 | `orbita_git_diff` | Consultar diferenças Git | readOnly: true |
| 9 | `orbita_prepare_file_change` | Preparar alteração de arquivo | readOnly: false, destrutivo: false |
| 10 | `orbita_apply_file_change` | Aplicar alteração aprovada | readOnly: false, destrutivo: true |
| 11 | `orbita_run_project_task` | Executar teste ou build autorizado | readOnly: false, destrutivo: true, openWorld: true |

**Resumo:** 11 ferramentas MCP (8 leitura + 3 escrita). As 3 escritas são: `orbita_set_workspace_root`, `orbita_prepare_file_change`, `orbita_apply_file_change`, `orbita_run_project_task`.

## 4. DEPENDÊNCIAS E REQUISITOS

### 4.1 Node.js

| Item | Valor |
|---|---|
| Versão atual | v26.12.1 |
| Requisito mínimo | Node.js 22.0.0 (LTS recomendado) |
| Verificação | ✅ `node --version` → v26.12.1 >= 22.0.0 |

### 4.2 Dependências do servidor (`server/package.json`)

| Dependência | Versão |
|---|---|
| `@modelcontextprotocol/server` | 2.4.0 |
| `zod` | 4.6.7 |

Ambas estão instaladas em `server/node_modules/`.

### 4.3 npm scripts

| Script | Comando |
|---|---|
| `start` | `node src/index.mjs` |
| `test` | `node --test test/*.test.mjs` |
| `check` | `node --check src/index.mjs && node --check src/tools.mjs && node --test test/*.test.mjs` |

## 5. PROTEGIÇÕES DE SEGURANÇA IMPLEMENTADAS

### 5.1 `server/src/security.mjs`

| Ameaça | Controle |
|---|---|
| Path traversal | Caminhos relativos ao workspace somente; `..` rejeitado |
| Symlink escape | Resolve caminho real e verifica contenção no workspace |
| Exposição de segredo | `.env*`, `.ssh`, `.git`, `node_modules`, tokens, credenciais, extensões de chave/certificado bloqueados |

### 5.2 `server/src/approvals.mjs`

| Controle | Descrição |
|---|---|
| Token de prévia | UUID, uso único, expira em 5 minutos |
| SHA-256 de concorrência | Verifica hash do conteúdo atual antes da gravação |

### 5.3 `server/src/workspace.mjs`

| Controle | Descrição |
|---|---|
| `isWithinRoot` | Verifica se caminho está dentro do workspace |
| `isSensitivePath` | Detecta arquivos sensíveis por nome e extensão |
| `resolveSafePath` | Resolve caminho, rejeita symlinks que escapam |
| `maxReadBytes` / `maxWriteBytes` | Limites de tamanho de arquivos |
| Detecção de NUL | Bloqueia arquivos binários |

### 5.4 `server/src/process.mjs`

| Controle | Descrição |
|---|---|
| `buildSafeEnvironment` | Exclui chaves de API, `NODE_OPTIONS` e variáveis privadas do ambiente do processo |
| Sem shell arbitrário | `shell: false` no child_process |

### 5.5 `server/src/tools.mjs`

| Controle | Descrição |
|---|---|
| `readOnlyHint` / `destructiveHint` / `openWorldHint` | Anotações de permissão para o host MCP |
| `register()` envolve cada handler em `try/catch` | Registrar erros no `audit.jsonl` e retorna `isError: true` |

## 6. FUNCIONALIDADES INCOMPLETAS

### 6.1 Faltantes

| Item | Status |
|---|---|
| **Testes MCP** | ❌ Não existem (apenas testes unitários) |
| **Testes de integração** | ❌ Não existem |
| **Instalador Windows Server** | ❌ Existe `scripts/Install-ORBITA.ps1` (instalação manual do plugin) — não é um instalador de serviço Windows nativo |
| **Serviço Windows** | ❌ Não implementado |
| **Documentação completa do plugin** | ❌ Base: README, security-model, technical-spec, skills |
| **Busca semântica** | ❌ Busca textual (case-insensitive) apenas |
| **Autenticação MCP** | ❌ Não há (depende do host aplicar permissões) |
| **Recuperação de falhas** | ❌ Estado perde em reinicialização (somente config.json persistido) |

### 6.2 Restrições documentadas

- STDIO somente (não SSE, não Streamable HTTP).
- Ambiente sandbox do host aplica permissões de aprovação.
- Separação STDOUT (JSON-RPC) / STDERR (diagnóstico).
- No método de aprovação do host: `writes` ou `prompt` recomendado.

## 7. DIAGNÓSTICO RESUMIDO

| Camada | Estado |
|---|---|
| Estrutura do projeto | ✅ Completa |
| Código-fonte | ✅ Lido e validado |
| Ferramentas MCP | ✅ 11 registradas |
| Dependências | ✅ Instaladas |
| Segurança | ✅ Implementada e testada |
| Testes unitários | ✅ 7/7 passam |
| Instalador Windows | ⚠️ Existe, mas não é serviço nativo |
| Testes MCP | ❌ Faltando |
| Testes de integração | ❌ Faltando |
| Serviço Windows | ❌ Faltando |
| Documentação completa | ⚠️ Parcial |

## 8. PRÓXIMOS PASSOS (FASE 1)

A partir deste diagnóstico, a arquitetura para o Windows Server deve ser desenvolvida seguindo o plano de entrega:

1. **FASE 1 — Arquitetura:** dois modos independentes (MCP STDIO e Serviço Windows Server).
2. **FASE 2 — Implementação:** desenvolver os componentes.
3. **FASE 3 — Segurança:** validar proteções.
4. **FASE 4 — Instalador:** criar instalador profissional.
5. **FASE 5 — Testes:** criar testes automatizados.
6. **FASE 6 — Documentação:** gerar documentação técnica.
7. **FASE 7 — Empacotamento final:** entregar versão.

**Critério final de liberação:** instalação, inicialização, segurança, ferramentas MCP e operação com evidências de validação.
