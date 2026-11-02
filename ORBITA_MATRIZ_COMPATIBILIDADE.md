# ORBITA_MATRIZ_COMPATIBILIDADE.md

**Versão do documento:** 1.0
**Data:** 31/10/2026
**Projeto:** ORBITA Universal Windows Server

---

## 1. OBJETIVO

Matriz de compatibilidade tecnológica para a ORBITA em ambiente Windows Server.

> **Aviso:** esta matriz identifica **compatibilidade teórica** e não **efetivamente testada**. Os testes no Windows Server 2019/2022/2025 não foram realizados neste ambiente.

---

## 2. PLATAFORMAS ALVO

| Plataforma | Versão | Suporte |
|---|---|---|
| Windows Server 2019 | 1809+ | Teórica |
| Windows Server 2022 | 21H2+ | Teórica |
| Windows Server 2025 | 24H2+ | Teórica |
| Node.js | 22.0.0+ | ✅ (requisito mínimo) |
| npm | ≥ 9.0.0 | ✅ (incluído com Node.js LTS) |
| PowerShell | 5.1+ | ✅ (incluído com Windows Server) |
| Git | ≥ 2.0 | ⚠️ Opcional (ferramentas Git) |

---

## 3. MATRIZ DE COMPATIBILIDADE

### 3.1 Compatibilidade plataforma × recurso

| Recurso | Windows Server 2019 | Windows Server 2022 | Windows Server 2025 |
|---|---|---|---|
| Node.js 22+ (LTS) | ✅ | ✅ | ✅ |
| npm ≥ 9 | ✅ | ✅ | ✅ |
| PowerShell 5.1+ | ✅ | ✅ | ✅ |
| Windows Service nativo | ✅ | ✅ | ✅ |
| sc.exe / PowerShell module | ✅ | ✅ | ✅ |
| File system NTFS | ✅ | ✅ | ✅ |
| Event Viewer | ✅ | ✅ | ✅ |
| Streamable HTTP (HTTP/1.1) | ✅ | ✅ | ✅ |
| Streamable HTTP (HTTP/2) | ❌ (HTTP/1.1) | ✅ (HTTP/2) | ✅ (HTTP/2) |
| Autenticação Bearer token | ✅ | ✅ | ✅ |
| Certificado X.509 | ✅ | ✅ | ✅ |
| Serviço auto-iniciar | ✅ | ✅ | ✅ |
| Log persistente | ✅ | ✅ | ✅ |
| Monitoramento (health check) | ✅ | ✅ | ✅ |
| Node.js sem root (skip) | ✅ | ✅ | ✅ |
| Sandbox (Windows Sandbox) | ❌ (não disponível no 2019/2022) | ❌ | ❌ |

### 3.2 Compatibilidade módulos × plataforma

| Módulo | Windows Server 2019 | Windows Server 2022 | Windows Server 2025 |
|---|---|---|---|
| `node:fs/promises` | ✅ | ✅ | ✅ |
| `node:child_process` | ✅ | ✅ | ✅ |
| `node:crypto` | ✅ | ✅ | ✅ |
| `node:http`/`https` | ✅ | ✅ | ✅ |
| `@modelcontextprotocol/server` 2.4.0 | ✅ | ✅ | ✅ |
| `zod` 4.6.7 | ✅ | ✅ | ✅ |
| `node:test` | ✅ | ✅ | ✅ |
| `node:v8` (diagnóstico) | ✅ | ✅ | ✅ |

---

## 4. RESTRIÇÕES

| Restrição | Impacto |
|---|---|
| **Windows Server 2019**: HTTP/2 não disponível | O Mode B usará HTTP/1.1 (funciona, mas sem vantagem de HTTP/2) |
| **Windows Server 2019**: Windows Sandbox não disponível | Não há sandbox isolado; a segurança do serviço depende das permissões NTFS |
| **Windows Server 2022/2025**: Segurança mais restritiva | Verificar Windows Security Baseline |
| **Node.js 22+**: Nenhum SDK nativo de TLS obsoleto | Certifique-se de não usar TLS desatualizado |
| **npm**: versões < 9 não são suportadas | Node.js LTS instalado por padrão | 

---

## 5. COMBINAÇÕES SUPERTESTADAS

Esta combinação foi testada no ambiente de desenvolvimento:

| Combinação | Status |
|---|---|
| Windows (desenvolvimento) + Node.js v26.12.1 + npm 11.20.0 | ✅ Validada |
| `@modelcontextprotocol/server` 2.4.0 + `zod` 4.6.7 | ✅ Validada |
| Servidor STDIO (11 ferramentas) | ✅ Validada (modo local) |

**NOTA:** as combinações de Windows Server 2019/2022/2025 **não foram testadas**. As descrições acima são baseadas em documentação pública e análise de requisitos.

---

## 6. COMBINAÇÕES DE NOSSO AMBIENTE

| Ambiente | Node.js | npm | Serviço | Status |
|---|---|---|---|---|
| Windows 11 (desenvolvimento) | v26.12.1 | 11.20.0 | STDIO | ✅ Validada |
| Windows Server 2019 | ? | ? | Serviço | ⚠️ Não testada |
| Windows Server 2022 | ? | ? | Serviço | ⚠️ Não testada |
| Windows Server 2025 | ? | ? | Serviço | ⚠️ Não testada |

---

## 7. RECOMENDAÇÕES

1. **Validar a compatibilidade** no ambiente de deploy.
2. **Verificar o Node.js** ≥ 22.0.0 (LTS recomendado).
3. **Verificar o Windows Security Baseline** nos servidores 2022/2025.
4. **Utilizar HTTP/1.1** no Windows Server 2019 (sem HTTP/2 nativo).
5. **Testar o serviço** (`node server/src/service.mjs`) antes de produção.

---

**Documento gerado em 31/10/2026.**
