# Progresso do ORBITA Universal Plugin

Atualizado: após o run Windows 41314619970
Branch: `work/windows-installer-validation`
Remoto: `80a1d28`; correção posterior está commitada localmente em `2008e9e`.

## Funcionalidades e estado

| Área | Estado | Evidência / pendência |
|---|---|---|
| MCP STDIO e handshake | CONCLUÍDA E VALIDADA localmente | Suíte de integração exercita handshake, descoberta e chamadas das ferramentas; asserção exige os nomes exatos das 11 ferramentas e chama `orbita_status`. 36 testes MCP passaram. |
| Proteção de workspace e diffs Git | CONCLUÍDA E VALIDADA em Linux | Testes de contenção, traversal e pathspec mágico; caminhos Windows/reparse points ainda pendentes. |
| Aprovação e gravação de arquivo | CONCLUÍDA E VALIDADA localmente | Preview/aplicação, hash e backup testados; teste adversarial de TOCTOU Windows pendente. |
| HTTP e autenticação | IMPLEMENTADA E VALIDADA por integração local | Token explícito e bind loopback; ainda não é o fluxo de distribuição STDIO. |
| TLS | IMPLEMENTADO, PARCIALMENTE VALIDADO | Teste cobre opções com credenciais resolvidas; handshake HTTPS real pendente. |
| Busca parcial | CONCLUÍDA E VALIDADA localmente | Falhas de I/O tornam resultado incompleto e contabilizam arquivos omitidos. |
| Tarefas npm/build/lint/typecheck | PARCIALMENTE IMPLEMENTADA | Desabilitadas por padrão; allowlist `npm-test` foi executada num fixture temporário após corrigir leitura dos scripts. Outras toolchains e sandbox permanecem pendentes. Scripts do workspace rodam sem sandbox. |
| Desktop Electron | IMPLEMENTADO, PARCIALMENTE VALIDADO | Sintaxe e manager testados; UI visual não foi validada neste Linux. |
| Revogação | PARCIALMENTE IMPLEMENTADA | Desktop agora persiste `workspaceRoot: null` sem criar diretório substituto; servidor ativo relê estado e bloqueia ferramentas com workspace. Testes validam arquivo original intacto e status MCP nulo; operação em andamento pode terminar. |
| Instalador Windows e Release | BUILD/SMOKE PARCIALMENTE VALIDADOS; RELEASE BLOQUEADA | Run [41314619970](https://github.com/epbfilmespedro-pixel/ORBITA-Universal-Plugin/actions/runs/41314619970) passou build e smoke funcional em Windows 11 x64, mas reportou `StandardUserInstall=BLOCKED` porque o runner é elevado (`releaseReady=false`). Alteração local agora cria conta não administrativa para repetir o smoke. Nenhuma Release foi publicada. |
| Integração ChatGPT Desktop oficial | BLOQUEADA POR AMBIENTE EXTERNO | Não há host oficial disponível para validação. |
| Atualização e reparo | NÃO IMPLEMENTADA | Funcionalidades documentadas como pendentes. |
| Histórico Git / branch | PARCIAL | Commits até `80a1d28` estão no branch remoto, evidenciado pelo run Windows 41314619970. O commit `2008e9e` está local e não pôde ser enviado: `git push` falhou por falta de senha/credencial. `main` permanece intocado. |

## Correções locais desta continuação

- Implementado workflow de tag para Release, validação SemVer contra `package.json`, publicação com `GITHUB_TOKEN` de escopo mínimo, um asset manual (instalador) e notas contendo SHA-256. Pré-lançamentos são publicados com o sinalizador de prerelease.
- Build e evidências foram separados em artefatos Actions; o job de publicação exige relatório Windows aprovado, binário PE, runtime win32/x64 e hash correspondente. Nenhuma tag ou Release foi criada.
- O run Windows 41314619970 passou parser PowerShell, checks, build NSIS x64 e smoke (MCP/11 ferramentas, UI, atalhos, desinstalação e persistência). O relatório revelou precisamente o gate restante: teste sob usuário não administrador foi bloqueado no runner elevado.
- O smoke foi ajustado localmente para criar uma conta padrão isolada e executar o teste com token não elevado; esse código ainda não foi executado no Windows.
- `npm test` passou com 36 testes MCP + 5 desktop; `npm run check`, parse dos dois YAMLs, validação `v0.1.0` e `npm audit --omit=dev` também passaram.
- A integração MCP exige o conjunto exato das 11 ferramentas anunciadas, schemas presentes e chama `orbita_status`.
- `npm test` passou com 36 testes MCP + 3 desktop; `npm --prefix orbita-agent/server run check` passou com 36 testes MCP.
- A execução real da tarefa npm com opt-in revelou e corrigiu erro de tipo: `packageInfo.scripts` é objeto, não array; validação agora usa `Object.hasOwn`. 36 testes MCP + 3 desktop passaram após a correção.
- A revogação desktop agora persiste `workspaceRoot: null` em vez de criar um workspace substituto; regressões confirmam que o workspace original permanece intacto e que chamadas seguintes MCP reportam autorização revogada.

## Bloqueios de conclusão

1. A correção recente do smoke está commitada em `2008e9e`, mas não foi enviada; autenticação não está configurada neste workspace (`gh auth status`).
2. O novo teste sob usuário padrão precisa passar no runner. O artifact atual é de runner elevado e não está aprovado para Release.
3. Nenhuma tag ou Release foi criada. Enviar `v0.1.0` somente após o relatório `releaseReady=true` e autenticação GitHub disponível.
4. Integração com ChatGPT Desktop oficial depende de acesso ao host e teste real; assinatura digital, reparo e atualização permanecem pendentes.
