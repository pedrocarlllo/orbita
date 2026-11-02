# ORBITA Universal Plugin

ORBITA combina um aplicativo desktop Electron para Windows com um servidor MCP local em Node.js. O aplicativo gerencia uma pasta autorizada, configurações e diagnóstico; o host MCP continua responsável por iniciar o servidor via STDIO.

> **Estado do produto:** a implementação desktop e o empacotamento estão em desenvolvimento. O código e os testes MCP foram validados neste ambiente Linux, mas a interface Electron não abriu por dependências gráficas ausentes, e a instalação Windows ainda aguarda validação no runner Windows. Não trate o instalador candidato como liberado.

## Arquitetura e segurança

- Interface local sem Node.js no renderer, com CSP, isolamento de contexto e IPC limitado.
- Servidor MCP STDIO iniciado pelo host compatível, não pelo dashboard.
- Nenhuma pasta de projeto é autorizada por padrão; selecione uma pasta específica no aplicativo.
- Leitura, pesquisa e escrita ficam limitadas ao workspace. Arquivos sensíveis, traversal e symlinks externos são bloqueados.
- Alterações são preparadas e aplicadas por token de uso único, com hash-base, backup e gravação atômica.
- O aplicativo gera e copia a configuração MCP; não modifica arquivos internos do ChatGPT.
- Tarefas npm predefinidas podem executar código definido pelo próprio projeto. Revise e aprove essas operações no host.

## Desenvolvimento e validação

Requisitos de desenvolvimento: Node.js 22 ou superior e npm.

```sh
npm ci
npm ci --prefix orbita-agent/server
npm test
npm run check
npm start
```

`npm start` abre a interface desktop quando o sistema possui os componentes gráficos exigidos pelo Electron.

## Instalador Windows

O build está configurado com electron-builder/NSIS, instalação por usuário, diretório selecionável, atalho do Menu Iniciar, opção de atalho na área de trabalho e preservação dos dados do usuário.

```sh
npm ci
npm ci --prefix orbita-agent/server
npm run dist:win
```

O workflow [.github/workflows/windows-installer.yml](./.github/workflows/windows-installer.yml) compila e executa um smoke test do instalador em `windows-latest`. O workflow [.github/workflows/release-windows.yml](./.github/workflows/release-windows.yml) valida tags SemVer e publica automaticamente o instalador como único asset manual da GitHub Release após os gates Windows. O instalador não é assinado. Consulte o [padrão de Releases](./docs/GITHUB_RELEASES_STANDARD.md) antes de versionar uma distribuição.

## Build e publicação

- [Guia de build](./BUILD.md)
- [Guia de Releases](./RELEASE.md)
- [Histórico de alterações](./CHANGELOG.md)

## Documentação

- [Auditoria do projeto](./docs/AUDIT_REPORT.md)
- [Arquitetura](./docs/ARCHITECTURE_REPORT.md)
- [Segurança e permissões](./docs/SECURITY_REPORT.md), [manual de permissões](./docs/PERMISSIONS.md)
- [Instalação](./docs/INSTALLATION.md), [utilização](./docs/USER_GUIDE.md)
- [Relatório do instalador](./docs/INSTALLER_REPORT.md)
- [Padrão de GitHub Releases](./docs/GITHUB_RELEASES_STANDARD.md)
- [Validação final e limitações](./docs/FINAL_VALIDATION_REPORT.md), [limitações conhecidas](./docs/KNOWN_LIMITATIONS.md)
