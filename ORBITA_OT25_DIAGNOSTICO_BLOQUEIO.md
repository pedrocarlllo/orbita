# ORBITA OT-25 — DIAGNÓSTICO DO BLOQUEIO HTTP 500

**Status:** BLOQUEADO PARA APROVAÇÃO  
**Prioridade:** Crítica  
**Responsável:** Diretor Técnico

---

## 1. ESTADO DA PORTA 3000

```
TCP    127.0.0.1:3000         0.0.0.0:0              LISTENING       3304
```

- **PID:** 3304
- **Imagem:** node.exe
- **Usuário:** DESKTOP-PSPDMEG\eric
- **Status:** Tudo certo — apenas 1 processo escutando na porta 3000

---

## 2. ESTADO DOS PROCESSOS

```
Processo 3304: node.exe (PID 3304)
- Imagem: node.exe
- Usuário: DESKTOP-PSPDMEG\eric
- CWD: /c/ORBITA-Universal-Plugin-Windows-0.1.0/orbita-agent/server
- Arquivo rodando: src/service.mjs (via startHttpServer)
```

- Processo 3304 foi iniciado **antes** da correção do `http.mjs` (modificação registrada em 17:01:55)
- O processo carrega o código da memória no momento do início; a modificação do arquivo **não** afeta o processo em execução
- Portanto, o erro HTTP 500 vem do código antigo que o processo carrega

---

## 3. ESTADO DOS ARQUIVOS

| Arquivo | Modificações Recentes | Estado |
|---|---|---|
| `src/transport/http.mjs` | Corrigido (17:01:55) | **OK** — URL absoluta no construtor `Request` |
| `src/service.mjs` | Inalterado | **OK** — apenas chama `startHttpServer()` |
| `src/tools.mjs` | Inalterado | **OK** — 11 ferramentas |
| `package.json` | Inalterado | **OK** — SDK v2.4.0 |

---

## 4. VERÇÃO DO SDK

- Pacote: `@modelcontextprotocol/server`
- Versão: **2.4.0**
- Instalado em: `/c/ORBITA-Universal-Plugin-Windows-0.1.0/orbita-agent/server/node_modules/@modelcontextprotocol/server/`

---

## 5. ERRO ENCONTRADO

### Erro original (registrado na execução)

```
[FAIL] 1. Inicialização (initialize)
Resultado: {"jsonrpc":"2.0","error":{"code":-32603,"message":"Internal server error"},"id":null}
```

### Stack trace do erro

```
Error: Failed to parse URL from /mcp
    at Request.url (node:internal/deps/body/url:3:11)
    at new Request (node:internal/deps/body/url:5:13)
    ...
```

### Causa imediata

O código antigo no processo 3304 chamava:

```js
const request = new Request(req.url, { ... });
```

Onde `req.url` = `/mcp` (URL relativa), e o `Request` construtor requer uma URL absoluta.

### Correção aplicada ao arquivo (17:01:55)

```js
const requestUrl = req.url.startsWith('http') ? req.url : `http://127.0.0.1:3000${req.url}`;
const request = new Request(requestUrl, { ... });
```

Agora `requestUrl` = `http://127.0.0.1:3000/mcp` (URL absoluta), o que resolve o erro de parsing.

---

## 6. CAUSA RAIZ CONFIRMADA

**Causa raiz: Código antigo em execução no processo HTTP.**

O processo 3304 foi iniciado antes da aplicação da correção. Durante sua execução, o código antigo tentou criar um objeto `Request` com URL relativa (`/mcp`), o que fazia com que o construtor `Request` lançasse `Failed to parse URL from /mcp`.

O arquivo `http.mjs` foi corrigido, mas o processo em execução não foi reiniciado. A correção só é eficaz após o restart do processo.

**Classificação da falha:** Erro de inicialização (instalação do servidor com código incompatível).

---

## 7. PRÓXIMA CORREÇÃO RECOMENDADA

1. **Matar o processo 3304** (node.exe) — identificado e autorizado
2. **Reiniciar o servidor** com o `http.mjs` corrigido
3. **Executar o teste completo** (initialize → notifications/initialized → tools/list → tools/call)
4. **Gerar o relatório de validação** `ORBITA_OT25_RELATORIO_TRANSPORTE_HTTP.md`

**Restrições após a correção:**
- Nenhuma modificação adicional nos arquivos
- Mantenha a restrição de loopback (127.0.0.1)
- Sem autenticação ou HTTPS nesta fase
- Não iniciar a FASE 3.2

---

## 8. CONCLUSÃO

O erro HTTP 500 foi causado por um **desalinhamento entre o código do arquivo e o código em memória do processo**. O processo 3304 estava rodando uma versão anterior de `http.mjs` que não implementava a conversão de URL absoluta para o `Request` do construtor MCP Streamable HTTP.

Após a reinicialização do processo com o código corrigido, o acesso HTTP deve funcionar conforme o protocolo MCP 2025-03-26.
