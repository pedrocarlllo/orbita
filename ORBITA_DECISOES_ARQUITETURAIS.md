# ORBITA_DECISOES_ARQUITETURAIS.md

**Versão do documento:** 1.0
**Data:** 31/10/2026
**Projeto:** ORBITA Universal Windows Server

---

## 1. OBJETIVO

Documentar decisões arquiteturais tomadas para a fase de desenvolvimento da ORBITA no Windows Server.

Para cada decisão, presente-se:

- **Contexto:** por que a decisão foi necessária
- **Alternativas:** opções consideradas
- **Vantagens:** prós da solução escolhida
- **Desvantagens:** contras da solução escolhida
- **Justificativa:** razão pela qual foi tomada

---

## 2. DECISÕES ARQUITETURAIS

### 2.1 Compartilhamento do núcleo

| Aspecto | Detalhe |
|---|---|
| **Alternativa A** | Núcleo compartilhado (`core/`) |
| **Alternativa B** | Duas implementações separadas (não duplicada) |
| **Número de ferramentas** | 11 (11 ferramentas registradas) |
| **Justificativa** | Manter um único código-fonte para todas as funcionalidades, reutilizando a lógica de segurança, aprovação, auditoria e workspace. Ditau que duplicar código acarretaria maior manutenção. |
| **Impacto** | Acoplamento fortalecido entre os modos; requer cuidado com mudanças que afetam o core. |

**Decisão:** usar **Alternativa A** — núcleo compartilhado no `server/src/core/`.

---

### 2.2 Transporte MCP

| Aspecto | Detalhe |
|---|---|
| **Alternativa A** | STDIO (Modo A — local) |
| **Alternativa B** | Streamable HTTP (Modo B — servidor) |
| **Alternativa C** | Streamable HTTP para ambos os modos |
| **Justificativa** | O Mode A mantém a compatibilidade existente (ChatGPT Desktop / Codex usam STDIO). O Mode B adota Streamable HTTP para suportar clientes remotos, pois HTTP/2 é disponível no Windows Server 2022+ e é natural para servidores. |
| **Impacto** | O Mode B requer autenticação de cliente; STDIO não tem (confia no sandbox do host). |

**Decisão:** Modo A = STDIO; Modo B = Streamable HTTP (quando disponível, HTTP/2).

---

### 2.3 Serviço Windows

| Aspecto | Detalhe |
|---|---|
| **Alternativa A** | Serviço nativo (sc.exe / PowerShell module) |
| **Alternativa B** | Script de agendamento do Windows |
| **Alternativa C** | Processo executado em segundo plano via PM2/supervisord (não nativo do Windows) |
| **Justificativa** | O serviço nativo do Windows é o mais apropriado para ambiente Windows Server, permitindo inicialização automática, tratamento de falhas e integração com o gerenciador de eventos. |
| **Impacto** | Requer registro via sc.exe ou PowerShell module; mais complexo que um script simples, mas mais robusto. |

**Decisão:** usar **Alternativa A** — serviço nativo via `sc.exe` ou PowerShell module `orbita-service`.

---

### 2.4 Autenticação

| Aspecto | Detalhe |
|---|---|
| **Alternativa A** | Bearer token (JWT ou similar) |
| **Alternativa B** | Certificado X.509 |
| **Alternativa C** | API key (simples) |
| **Justificativa** | O Bearer token é simples, flexível e amplamente suportado. Para produção, o certificado pode ser usado. |
| **Impacto** | A implementação ainda não está disponível no código atual. Elaboração pendente. |

**Decisão:** projetar com Bearer token (ou certificado no estágio de produção). Implementação futura.

---

### 2.5 Autorização por ferramenta

| Aspecto | Detalhe |
|---|---|
| **Alternativa A** | Usar anotações MCP (`readOnlyHint`, `destructiveHint`, `openWorldHint`) |
| **Alternativa B** | Política exclusiva do ORBITA |
| **Justificativa** | As anotações MCP são o padrão e são lidas pelo host; a política de aprovação do ORBITA complementa com regras mais granulares. |
| **Impacto** | A autorização requer configuração no host e no servidor. |

**Decisão:** usar **anotações MCP + política de aprovação do ORBITA**.

---

### 2.6 Logs

| Aspecto | Detalhe |
|---|---|
| **Alternativa A** | Console (STDOUT/STDERR) |
| **Alternativa B** | Arquivo de log no `%PROGRAMDATA%\ORBITA\logs\` |
| **Alternativa C** | Event Viewer (Windows) |
| **Justificativa** | O log no filesystem é a solução mais acessível e está disponível em todos os ambientes Windows Server. O Event Viewer pode ser usado como complemento. |
| **Impacto** | Requer rotacionamento de logs. |

**Decisão:** usar **arquivo de log** no `%PROGRAMDATA%\ORBITA\logs\` + Event Viewer complementar.

---

### 2.7 Persistência

| Aspecto | Detalhe |
|---|---|
| **Alternativa A** | `config.json` (existente) |
| **Alternativa B** | Banco de dados (SQLite/PostgreSQL) |
| **Alternativa C** | Arquivo JSON personalizado |
| **Justificativa** | O `config.json` já é usado no código atual. Não há necessidade de banco de dados para um projeto de 0.1.0. |
| **Impacto** | Manter forma de arquivo; sem escala horizontal. |

**Decisão:** manter **config.json** + auditoria JSONL; sem banco de dados.

---

### 2.8 Atualizações

| Aspecto | Detalhe |
|---|---|
| **Alternativa A** | Atualização manual (backup + reinstalação) |
| **Alternativa B** | Atualização automática (feed de atualização) |
| **Justificativa** | Como padrão, usar atualização manual com backup. A automação será definida em uma fase futura. |
| **Impacto** | Requer acesso manual ao servidor para atualização. |

**Decisão:** **atualização manual** com backup; fase futura contemplate.

---

### 2.9 Instalação

| Aspecto | Detalhe |
|---|---|
| **Alternativa A** | `Install-ORBITA.ps1` (existente) |
| **Alternativa B** | `Install-Service.ps1` (novo) |
| **Justificativa** | O `Install-ORBITA.ps1` já é usado no desktop. Para servidores, estender com modo `--service` que registra o serviço Windows. |
| **Impacto** | Novos scripts de instalação; sem alteração dos existentes. |

**Decisão:** estender `Install-ORBITA.ps1` com `--service` e criar `Install-Service.ps1` (não realizadas neste estágio).

---

### 2.10 Recuperação de falhas

| Aspecto | Detalhe |
|---|---|
| **Alternativa A** | Restart automático (SCM) |
| **Alternativa B** | Logs de erro (monitoramento) |
| **Alternativa C** | Monitoramento ativo (health check) |
| **Justificativa** | A combinação de restart automático + health check é robusta e simples, sem depender de tools externos. |
| **Impacto** | Nenhuma dependência de ferramentas extras. |

**Decisão:** usar **restart automático + health check + logs persistentes**.

---

### 2.11 Ferramentas MCP (conteúdo)

| Aspecto | Detalhe |
|---|---|
| **Alternativa A** | As 11 ferramentas existentes |
| **Alternativa B** | 19 ferramentas (conteúdo original) |
| **Justificativa** | A contagem correta é **11 ferramentas**, conforme `server/src/tools.mjs`. As 8 "faltantes" não existem no código. |
| **Impacto** | O inventário correto é essencial para a validação de integração. |

**Decisão:** manter **11 ferramentas MCP** (exatamente como registradas em `server/src/tools.mjs`).

---

## 3. RESUMO DAS DECISÕES

| # | Decisão | Escolha |
|---|---|---|
| 1 | Compartilhamento do núcleo | Núcleo compartilhado (`core/`) |
| 2 | Transporte MCP | STDIO (Modo A) + Streamable HTTP (Modo B) |
| 3 | Serviço Windows | Serviço nativo (`sc.exe` / PowerShell module) |
| 4 | Autenticação | Bearer token / certificado (implementação futura) |
| 5 | Autorização | Anotações MCP + política de aprovação |
| 6 | Logs | Arquivo (`%PROGRAMDATA%\ORBITA\logs\`) + Event Viewer |
| 7 | Persistência | `config.json` + auditoria JSONL |
| 8 | Atualizações | Manual (backup) |
| 9 | Instalação | `Install-ORBITA.ps1` (desktop) + `--service` (servidores) |
| 10 | Recuperação | Restart automático + health check |
| 11 | Ferramentas MCP | 11 ferramentas (conforme `tools.mjs`) |

---

## 4. RISCOS E DEPENDÊNCIAS

| Risco | Nível | Dependência |
|---|---|---|
| Redundância de código ao implementar os dois modos | Médio | Design cuidadoso do núcleo compartilhado |
| Segurança de transporte (HTTP/2, certificados) | Alto | Implementação futura da autenticação |
| Licença do Node.js em ambientes corporativos | Baixo | Verificar compatibilidade |
| Windows Server 2019 sem HTTP/2 | Médio | Usar HTTP/1.1 no 2019 |
| Acesso a logs no Windows Server 2019 | Baixo | Event Viewer disponível |

---

**Documento gerado em 31/10/2026.**
