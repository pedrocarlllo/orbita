# Próximo passo exato

1. Autenticar GitHub no workspace e enviar o commit local `2008e9e` do branch `work/windows-installer-validation`; o push atual falhou por credencial ausente.
2. Exigir que a execução Windows teste sob conta local não administrativa e gere `releaseReady=true`.
3. Apenas depois desse gate, enviar a tag `v0.1.0` (versão atual de `package.json`), se ainda não existir, para disparar build/release. O job de publicação verifica PE, versão, arquitetura e SHA-256 antes de anexar o `.exe`.
4. Confirmar a Release e o asset publicado na página GitHub Releases. Não afirmar integração com ChatGPT Desktop oficial sem teste com o host.
