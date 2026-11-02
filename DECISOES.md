# Decisões técnicas do ORBITA

Atualizado: 2026-11-01 13:28 UTC

| Data | Decisão | Motivo / consequência |
|---|---|---|
| 2026-11-01 | Preservar branch `work/windows-installer-validation` e não reconciliar `main` sem autorização específica | `main` local diverge do remoto e o branch de trabalho contém commit local e alterações não commitadas. Não fazer merge, rebase, reset, pull ou push implicitamente. |
| 2026-11-01 | Manter MCP STDIO como integração principal; HTTP/TLS permanece caminho separado | Host MCP inicia o servidor por STDIO; HTTP requer credencial explícita e validação adicional. Não representar self-test como conexão com ChatGPT. |
| 2026-11-01 | Manter execução de tarefas de projeto desabilitada por padrão | Scripts npm podem executar código e acessar recursos do usuário; allowlist não é sandbox. Habilitação requer `ORBITA_ALLOW_PROJECT_TASKS=true`. |
| 2026-11-01 | Usar pathspec literal para comandos Git e preservar filtragem de arquivos sensíveis | Evita interpretação de nomes controlados como pathspec magic; regressão automatizada cobre staged e unstaged em Linux. |
| 2026-11-01 | Revalidar workspace persistido antes de cada chamada MCP | Permite que revogação/alteração bloqueie chamadas subsequentes de processo MCP ativo. Uma operação já iniciada não pode ser cancelada retroativamente. |
| 2026-11-01 | Não declarar build Linux como validação do instalador Windows | Tentativa terminou com `wine process failed ENOENT`; arquivos parciais foram removidos. Só runner Windows prova instalação e desinstalação. |
| 2026-11-01 | Preservar evidência histórica no relatório técnico e acrescentar estado de remediação | Evita reescrever resultados antigos como se tivessem sido obtidos após as correções. |
| 2026-11-01 | Revogar workspace persistindo `workspaceRoot: null`, sem diretório substituto | Remove autorização em vez de manter um workspace vazio artificial; testes confirmam negação em chamadas MCP subsequentes e preservação do diretório autorizado original. |
| 2026-11-01 | Validar scripts npm por chave de objeto | `package.json.scripts` é um objeto; `Object.hasOwn` corrige a execução explicitamente habilitada e retorna erro claro para script ausente. |
| 2026-11-01 | Separar build Windows reutilizável do workflow de publicação por tag | Evita compilações duplicadas e limita `contents: write` ao job de Release; validação e build permanecem somente leitura. |
| 2026-11-01 | Publicar somente o setup como asset manual e manter evidências como artifact Actions | SHA-256 e evidências ficam verificáveis sem anexar logs; os arquivos Source code continuam sendo gerados automaticamente pelo GitHub. |
| 2026-11-01 | Não criar tag/Release antes da validação real no runner Windows | O build local Linux não valida o instalador; manter publicação bloqueada até smoke aprovado e autenticação disponível. |
