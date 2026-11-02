# ORBITA_PLANO_IMPLEMENTACAO.md

**Versão do documento:** 1.0
**Data:** 31/10/2026
**Projeto:** ORBITA Universal Windows Server

---

## 1. OBJETIVO

Plano de implementação dividido em etapas para transformar a ORBITA em uma plataforma compatível com Windows Server, preservando o projeto existente.

**Critério de aprovação da Fase 1:** todos os seis documentos entregues (arquivo arquitetura, diagrama, decisões, matriz, plano de segurança, plano de implementação).

---

## 2. ESTRUTURA DOCUMENTOS CAMINHO

| Documento | Autor | Status |
|---|---|---|
| ORBITA_ARQUITETURA_WINDOWS_SERVER.md | Arquitetura | ✅ Entregue |
| ORBITA_DIAGRAMA_ARQUITETURAL.md | Arquitetura | ✅ Entregue |
| ORBITA_DECISOES_ARQUITETURAIS.md | Arquitetura | ✅ Entregue |
| ORBITA_MATRIZ_COMPATIBILIDADE.md | Arquitetura | ✅ Entregue |
| ORBITA_PLANO_SEGURANCA.md | Segurança | ✅ Entregue |
| ORBITA_PLANO_IMPLEMENTACAO.md | Engenharia | ✅ Entregue |

---

## 3. FASES DE IMPLEMENTAÇÃO

### FASE 1 — Arquitetura (ENTREGUE)

**Entregas:**

1. ORBITA_ARQUITETURA_WINDOWS_SERVER.md
2. ORBITA_DIAGRAMA_ARQUITETURAL.md
3. ORBITA_DECISOES_ARQUITETURAIS.md
4. ORBITA_MATRIZ_COMPATIBILIDADE.md
5. ORBITA_PLANO_SEGURANCA.md
6. ORBITA_PLANO_IMPLEMENTACAO.md

**Objetivos:**

- Definir dois modos independentes (MCP STDIO + Serviço Windows)
- Especificar núcleo compartilhado
- Documentar modelo de segurança
- Projetar serviço Windows
- Justificar transporte remoto
- Dividir plano de implementação em etapas

**Resultado:** arquitetura definida; validação da fase 1.

---

### FASE 2 — Implementação do núcleo compartilhado

**Objetivos:**

- Criar `server/src/core/` com:
  - `registry.mjs` (registro de ferramentas)
  - `workspace.mjs` (gestão de workspace)
  - `security.mjs` (sistema de segurança — reutiliza o existente)
  - `approvals.mjs` (sistema de aprovações — reutiliza o existente)
  - `audit.mjs` (auditoria — reutiliza o existente)
  - `process.mjs` (controle de processos — reutiliza o existente)
- Reorganizar `server/src/tools.mjs` para usar o core
- Criar `server/src/transport/stdio.mjs` (Modo A)
- Criar `server/src/transport/streamable-http.mjs` (Modo B)

**Tarefas:**

1. Criar pasta `server/src/core/` e mover `security.mjs`, `approvals.mjs`, `audit.mjs`, `process.mjs`
2. Criar `registry.mjs` (registro de ferramentas)
3. Reorganizar `state.mjs` para espaço de trabalho
4. Criar `transport/stdio.mjs` (Modo A)
5. Criar `transport/streamable-http.mjs` (Modo B)
6. Criar `server/src/service.mjs` (entry point do Modo B)

**Entregas:**

- `server/src/core/registry.mjs`
- `server/src/transport/stdio.mjs`
- `server/src/transport/streamable-http.mjs`
- `server/src/service.mjs`

---

### FASE 3 — Implementação de transporte

**Objetivos:**

- Implementar transporte STDIO (Modo A)
- Implementar transporte Streamable HTTP (Modo B)
- Validar ambos os transportes

**Tarefas:**

1. Implementar `stdio.mjs` (Modo A)
2. Implementar `streamable-http.mjs` (Modo B)
3. Escrever testes de transporte
4. Validar 11 ferramentas em ambos os modos

**Entregas:**

- `server/src/transport/stdio.mjs`
- `server/src/transport/streamable-http.mjs`
- Testes de transporte

---

### FASE 4 — Segurança

**Objetivos:**

- Implementar autenticação (Bearer token / certificado)
- Implementar autorização por ferramenta
- Configurar permissões NTFS
- Implementar HTTPS (TLS)

**Tarefas:**

1. Implementar autenticação (Bearer token)
2. Implementar autorização (policy.mjs)
3. Configurar permissões NTFS
4. Implementar HTTPS (TLS)

**Entregas:**

- `server/src/security/auth.mjs`
- `server/src/security/policy.mjs`
- Configuração NTFS
- Configuração HTTPS

---

### FASE 5 — Instalador

**Objetivos:**

- Expandir `Install-ORBITA.ps1` para incluir modo `--service`
- Criar `Install-Service.ps1`
- Criar `Uninstall-Service.ps1`
- Implementar backup/recovery

**Tarefas:**

1. Implementar `Install-Service.ps1` (registro do serviço)
2. Implementar `Uninstall-Service.ps1`
3. Implementar backup/recovery
4. Testar instalação no Windows Server

**Entregas:**

- `scripts/Install-Service.ps1`
- `scripts/Uninstall-Service.ps1`
- Documentação de instalação

---

### FASE 6 — Testes

**Objetivos:**

- Criar testes de unidade para núcleo
- Criar testes de transporte
- Criar testes de segurança
- Criar testes de serviço HTTP

**Tarefas:**

1. Implementar testes de núcleo (`server/test/core.test.mjs`)
2. Implementar testes de transporte (`server/test/transport.test.mjs`)
3. Implementar testes de segurança (`server/test/auth.test.mjs`)
4. Implementar testes de serviço (`server/test/service.test.mjs`)

**Entregas:**

- `server/test/core.test.mjs`
- `server/test/transport.test.mjs`
- `server/test/auth.test.mjs`
- `server/test/service.test.mjs`

---

### FASE 7 — Documentação

**Objetivos:**

- Gerar documentação técnica
- Gerar documentação de instalação
- Gerar documentação de administração

**Tarefas:**

1. Gerar documentação de arquitetura
2. Gerar documentação de instalação
3. Gerar documentação de administração
4. Publicar documentação (GitHub/Confluence)

**Entregas:**

- `README.md` atualizado
- `INSTALL_WINDOWS_SERVER.md`
- `SECURITY.md`
- `CHANGELOG.md`

---

### FASE 8 — Empacotamento final

**Objetivos:**

- Empacotar projeto (ZIP/NSIS)
- Preparar repositório
- Preparar release

**Tarefas:**

1. Criar script de empacotamento
2. Criar release notes
3. Publicar release

**Entregas:**

- `ORBITA-WINDOWS-SERVER.zip` (ou equivalente)
- Release notes

---

## 4. PLANO DE TRABALHO DETALHADO

| Ordem | Tarefa | Entregável | Dependências |
|---|---|---|---|
| 1 | Arquitetura (6 documentos) | 6 PDFs/MD | Diagnóstico (Fase 0) |
| 2 | Núcleo compartilhado | `core/*.mjs` | Arquitetura |
| 3 | Transporte STDIO | `transport/stdio.mjs` | Núcleo |
| 4 | Transporte Streamable HTTP | `transport/streamable-http.mjs` | Núcleo |
| 5 | Service entry point | `service.mjs` | Núcleo + Transportes |
| 6 | Autenticação | `security/auth.mjs` | Arquitetura |
| 7 | Autorização | `security/policy.mjs` | Arquitetura |
| 8 | Permissões NTFS | Script PowerShell | Arquitetura |
| 9 | HTTPS (TLS) | Configuração | Autenticação |
| 10 | Instalador de serviço | `Install-Service.ps1` | Arquitetura |
| 11 | Testes do núcleo | `test/core.test.mjs` | Núcleo |
| 12 | Testes de transporte | `test/transport.test.mjs` | Transportes |
| 13 | Testes de segurança | `test/auth.test.mjs` | Segurança |
| 14 | Testes de serviço | `test/service.test.mjs` | Serviço + HTTP |
| 15 | Documentação final | README/INSTALL/CHANGELOG | Todas |
| 16 | Empacotamento | Release package | Tempo |

---

## 5. RITMO DE TRABALHO

| Fase | Entregável | Duração sugerida |
|---|---|---|
| Fase 1 — Arquitetura | 6 documentos | 1 dia |
| Fase 2 — Núcleo compartilhado | `core/*.mjs` | 1–2 dias |
| Fase 3 — Transporte | `transport/*.mjs` | 1–2 dias |
| Fase 4 — Segurança | `security/*.mjs` + NTFS + HTTPS | 1–2 dias |
| Fase 5 — Instalador | `Install-Service.ps1` | 1 dia |
| Fase 6 — Testes | `test/*.test.mjs` | 1–2 dias |
| Fase 7 — Documentação | README/INSTALL/CHANGELOG | 1 dia |
| Fase 8 — Empacotamento | Release package | 1 dia |

---

## 6. CRITÉRIOS DE ACEITAÇÃO

| Item | Critério |
|---|---|
| 1. Dois modos | Modo A (STDIO) e Modo B (Serviço) entregues |
| 2. Núcleo compartilhado | `core/` implementado |
| 3. Modelo de segurança | Documentado e implementado |
| 4. Serviço Windows | Entregue e funcionando |
| 5. Transporte remoto | Streamable HTTP implementado e testado |
| 6. Plano de implementação | Dividido em etapas (este documento) |
| 7. Documentos | Todos os 6 entregues |

---

## 7. RISCOS

| Risco | Impacto | Mitigação |
|---|---|---|
| Implementação dos dois modos duplica código | Médio | Núcleo compartilhado |
| Segurança da transporte remota | Alto | Autenticação + HTTPS |
| Compatibilidade Windows Server 2019 | Médio | HTTP/1.1 (sem HTTP/2) |
| Tempo de implementação | Médio | Planejamento cuidadoso |
| Testes da instalação | Médio | Testes automatizados |

---

**Documento gerado em 31/10/2026.**
