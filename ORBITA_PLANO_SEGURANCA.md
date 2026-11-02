# ORBITA_PLANO_SEGURANCA.md

**Versão do documento:** 1.0
**Data:** 31/10/2026
**Projeto:** ORBITA Universal Windows Server

---

## 1. OBJETIVO

Documentar o plano de segurança para a ORBITA no Windows Server, incluindo:

- Identidade do serviço Windows
- Privilégios mínimos
- Permissões NTFS
- Isolamento entre usuários e workspaces
- Proteção de credenciais
- Autenticação dos clientes remotos
- Autorização por ferramenta
- Proteção contra acesso externo indevido
- Registro de operações
- Política de aprovação de escrita e execução

---

## 2. IDENTIDADE DO SERVIÇO

### 2.1 Conta de execução

| Item | Recomendação |
|---|---|
| Conta padrão | **NÃO usar SYSTEM** |
| Conta recomendada | **CA_OU_USUARIO_LIMPO** (least privilege) |
| Criação | Automática em instalação |
| Regras de inclusão | Contas de servidores sem permissões necessárias devem usar a conta de servidor |

**Justificativa:** executar como SYSTEM amplifica o risco de ataques maliciosos que exploram vulnerabilidades no ORBITA ou no sistema.

### 2.2 Permissões NTFS

| Entidade | Permissão | Justificativa |
|---|---|---|
| Folders de workspace do usuário | **Leitura somente** (padrão) | O ORBITA não deve gravar arquivos do workspace sem prévia e aprovação |
| `config.json` | Leitura/escrita (somente o serviço) | Configuração de serviço |
| `audit.jsonl` | Leitura/escrita (somente o serviço) | Auditoria |
| `logs/` | Leitura/escrita (somente o serviço) | Logs do serviço |
| Scripts de instalação | Somente administrador | Instalação |
| Node.js executável | Somente leitura | Execução |
| server/src/* | Somente leitura (não modificável) | Código-fonte |

**Justificativa:** limitar permissões NTFS reduz o escopo de possível comprometimento.

---

## 3. ISOLAMENTO ENTRE USUÁRIOS E WORKSPACES

### 3.1 Conta de serviço

A ORBITA deve executar com **conta de baixo privilégio**:

- **Windows Server 2019/2022/2025:** conta local (ex: `orbita-service`) sem privilégios elevados
- **User workspace isolation:** cada workspace no serviço é isolado por diretório

### 3.2 Isolamento do workspace

```
C:\ProgramData\ORBITA\
├── data/
│   ├── config.json
│   ├── audit.jsonl
│   └── logs/
└── workspace/          ← Root de workspaces
    ├── user1/
    ├── user2/
    └── ...
```

Cada usuário tem um workspace separado; o ORBITA não tem acesso direto a outros workspaces do sistema.

---

## 4. PROTECÇÃO DE CREDENCIAIS

| Tipo | Política |
|---|---|
| Chaves de API (OpenAI, GitHub, AWS) | **Não armazenar** no disco; apenas no ambiente do processo ao executar |
| Tokens de sessão | Nunca persistir em `config.json` |
| Credenciais do serviço | Usar `sc.exe` para proteger a conta do serviço |
| Variáveis de ambiente | Usar `process.mjs` (buildSafeEnvironment) para limpar variáveis sensíveis |

**Justificativa:** a proteção não é baseada em criptografia, mas na ausência de armazenamento.

---

## 5. AUTENTICAÇÃO DOS CLIENTES REMOTOS

| Item | Etapa | Status |
|---|---|---|
| Bearer token | Implementar no service.mjs | 🚧 Projeto (não em produção) |
| Certificado X.509 | Implementar no service.mjs | 🚧 Projeto (não em produção) |
| API key | Avançar (modo legacy) | 🚧 Projeto (não em produção) |
| Verificação de origem (IP Allowlist) | Opcional (quando ativável) | 🚧 Projeto (não em produção) |

**Justificativa:** autenticação ainda pendente de implementação.

---

## 6. AUTORIZAÇÃO POR FERRAMENTA

### 6.1 Políticas de aprovação

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

### 6.2 Regras de autorização no serviço HTTP

```
Requisição /mcp
   │
   ▼
Verificar autenticação
   │
   ▼
Verificar autorização (leitura/escrita/execução)
   │
   ▼
Executar handler
   ├── Verificar workspace
   ├── Verificar path traversal
   ├── Verificar segredos
   ├── Executar operação
   └── Registar auditoria (audit.jsonl)
```

---

## 7. PROTECÇÃO CONTRA ACESSO EXTERNO INDEVIDO

| Controle | Descrição |
|---|---|
| Network isolation | O serviço só escuta em `127.0.0.1` por padrão |
| Porta de configuração | HTTP 3000 (configurável) |
| IP Allowlist | Quando suportável |
| Rate limiting | Limitar requisições (implementação futura) |
| HTTPS only | Recomendado em produção (TLS) |
| Segurança da autenticação | Bearer token / certificado |

---

## 8. REGISTRO DE OPERAÇÕES

### 8.1 Auditoria (audit.jsonl)

| Campo | Descrição |
|---|---|
| timestamp | Data/hora RFC3339 |
| action | Nome da ferramenta |
| outcome | success/failure |
| path | Caminho do arquivo (se aplicável) |
| task | Tarefa executada (se aplicável) |
| bytes | Tamanho em bytes (se aplicável) |

**Politica:** metadados somente; nenhum conteúdo, credenciais ou variaveis de ambiente são registrados.

### 8.2 Logs do serviço

| Arquivo | Descrição |
|---|---|
| `%PROGRAMDATA%\ORBITA\logs\orbita-service.log` | Log de rotina do serviço |
| `%PROGRAMDATA%\ORBITA\logs\orbita-error.log` | Log de erros |

---

## 9. POLÍTICA DE APROVAÇÃO DE ESCRITURA E EXECUÇÃO

### 9.1 Políticas para ferramentas de escrita

| Ferramenta | Aprovação |
|---|---|
| `orbita_set_workspace_root` | Modal de confirmação do host (altera o workspace ativo) |
| `orbita_prepare_file_change` | Prévia (não grava); mostrar resumo; aguardar aprovação |
| `orbita_apply_file_change` | Aprovação do host (não usar autoaprovação) |
| `orbita_run_project_task` | Aprovação explícita do host (executa código do projeto) |

### 9.2 Políticas para ferramentas de leitura

| Ferramenta | Aprovação |
|---|---|
| `orbita_status` | Nenhuma |
| `orbita_list_files` | Nenhuma |
| `orbita_read_file` | Nenhuma |
| `orbita_search_files` | Nenhuma |
| `orbita_inspect_project` | Nenhuma |
| `orbita_git_status` | Nenhuma |
| `orbita_git_diff` | Nenhuma |

---

## 10. MÉTRICAS DE SEGURANÇA

| Métrica | Valor | Status |
|---|---|---|
| Número de ferramentas | 11 | ✅ |
| Path traversal | Bloqueado | ✅ |
| Symlink escape | Bloqueado | ✅ |
| Segredos (por nome/extensão) | Bloqueados | ✅ |
| Limites de bytes de leitura | `maxReadBytes` | ✅ |
| Limites de bytes de escrita | `maxWriteBytes` | ✅ |
| Environment filter | `buildSafeEnvironment` | ✅ |
| Aprovação de tokens | UUID único, 5 min | ✅ |
| Auditoria | JSONL | ✅ |
| Serviço | Conta de baixo privilégio | 🚧 Projeto |
| Autenticação | Pendente implementação | 🚧 Projeto |
| HTTPS | Recomendado (TLS) | 🚧 Projeto |

---

## 11. PRÓXIMOS PASSOS

1. Implementar autenticação (Bearer token/certificado).
2. Definir conta de serviço com baixo privilégio.
3. Configurar permissões NTFS.
4. Ativar HTTPS (TLS) em produção.
5. Implementar rate limiting.
6. Implementar HTTP/2 (no Windows Server 2022+).

---

**Documento gerado em 31/10/2026.**
