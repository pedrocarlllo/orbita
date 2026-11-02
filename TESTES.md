# Registro de testes do ORBITA

Atualizado: 2026-11-01 13:45 UTC

Ambiente local: Linux x86_64, Node.js 24.22.2, npm 11.19.1.

## Execuções registradas

| Comando | Resultado | Observação |
|---|---|---|
| `npm test` | PASS — 36 MCP + 5 desktop; 0 falhas, 0 ignorados | Inclui os testes de SemVer/tag Release, lista exata das 11 ferramentas e tarefa `npm-test` com opt-in em fixture temporário. |
| `npm --prefix orbita-agent/server run check` | PASS — sintaxe e 36 testes MCP | Reexecutado após reforçar respostas de revogação e tarefa npm. |
| `npm run check` e `node --check` dos módulos MCP principais | PASS | Sintaxe dos processos Electron, preload, renderer, entry point, tools, HTTP e TLS. |
| `node --check` em entry point MCP, tools, HTTP e TLS | PASS | Validação sintática dos módulos centrais. |
| `npm audit --omit=dev` (raiz e servidor) | PASS — zero vulnerabilidades reportadas | Escopo: dependências de produção consultadas. |
| Resolução do diretório release nos scripts PowerShell | PASS em verificação equivalente Linux; runtime Windows pendente | Os scripts derivam `desktop/scripts/../..` para o root do repo. Workflow também invoca smoke em `-ValidatePathsOnly`, executa o writer e exige o JSON no caminho esperado antes do build. PowerShell não está instalado localmente. |
| `npm ls --depth=0` (raiz e servidor) | PASS | Dependências diretas resolvidas. |
| `git -c core.whitespace=cr-at-eol diff --check` | PASS | Trata CRLF preexistente/adotado no `workspace-manager.mjs`. |
| Parse YAML de ambos os workflows Windows | PASS | PyYAML `safe_load`; não valida semântica GitHub Actions. |
| `node scripts/validate-release-version.mjs v0.1.0` | PASS | Tag corresponde à versão atual de `package.json`; testes cobrem inválida e divergente. |
| `npm audit --omit=dev` (raiz) | PASS — zero vulnerabilidades reportadas | Auditoria das dependências de produção consultadas nesta execução. |
| `git diff --check` | PASS | Sem erros de whitespace nas mudanças atuais. |
| `npm run dist:win` | FAIL — exit 1, `wine process failed ENOENT` | Linux sem Wine; build não validou nem produziu instalador final. Diretório `release/` parcial foi removido após inspeção. |
| `git push origin HEAD:refs/heads/work/windows-installer-validation` | BLOQUEADO — `fatal: unable to get password from user` | Push foi expressamente aprovado; `gh auth status` confirmou que não há login configurado. Nenhum dado foi enviado ao remoto. |
| `gh auth status` + `git -c 'credential.helper=!gh auth git-credential' push ...` | BLOQUEADO — `You are not logged into any GitHub hosts` | Tentativa repetida após o usuário confirmar autenticação; credenciais continuam indisponíveis neste workspace. Nenhum dado enviado. |
| Push do fix `96d4f04` | BLOQUEADO — `fatal: unable to get password from user` | Commit permaneceu local; `origin/work/windows-installer-validation` está em `3856749`. |
| `npm ci` | NÃO EXECUTADO | Lockfiles/manifests não mudaram e dependências já estavam instaladas. |
| Smoke de instalação Windows | PENDENTE | Precisa de runner Windows após enviar candidato. |
| Workflow de Release automática | PENDENTE | YAML e validador SemVer passaram localmente; o workflow de tag ainda não foi executado. Não há Release publicada. |
| Run Windows `41314619970` | PARCIAL | Parser, build e smoke passaram; suíte teve 35 MCP aprovados, 1 ignorado, 0 falhas e 5 desktop aprovados. Artifact setup 123,366,193 bytes, SHA-256 `465C944253EFB1F576F57AA2B80A26380F98979C2B8F390794A90C65F00B8716`. Relatório `releaseReady=false` porque `StandardUserInstall=BLOCKED` sob runner elevado. |
| Smoke em token de usuário padrão | PENDENTE | Implementado teste com conta local fora do grupo Administrators; precisa de rerun Windows. |
| Push atual do branch | BLOQUEADO | Commits até `80a1d28` estão no remoto; o commit de correção `2008e9e` está local. Push falhou com `fatal: unable to get password from user`; `gh auth status` não encontra login. |
| ChatGPT Desktop oficial | PENDENTE | Host oficial indisponível neste ambiente. |
| Job 124865182940 / writer PowerShell | FALHA reportada pelo usuário | Erro em `WriteAllText`: caminho para `release/windows-validation-report.json` não existia. Consulta à API GitHub nesta sessão retornou 404 para o run; análise baseada nos detalhes/log fornecidos pelo usuário. |

## Regressão de ferramentas MCP

A integração STDIO compara o conjunto exato de onze ferramentas, verifica schemas de entrada e invoca `orbita_status`, inclusive após remover a autorização persistida. Uma regressão executa `orbita_run_project_task` com `ORBITA_ALLOW_PROJECT_TASKS=true` num workspace descartável e script controlado; também comprova que tarefa ausente retorna erro explícito. O teste detectou `npmScripts.includes is not a function`; corrigiu-se a consulta das chaves do objeto `scripts`. Uma primeira asserção da resposta negativa falhou porque comparava regex com o JSON serializado (`\\"build\\"`) em vez de analisar `error`; passou a fazer parse do conteúdo JSON e a suíte foi repetida com sucesso. A suíte desktop confirma revogação com `workspaceRoot: null`, sem diretório substituto e sem tocar no arquivo do workspace original. As suítes completas passaram depois das correções.
