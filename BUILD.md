# Build guide

## Requirements

- Node.js 24 (the CI workflow uses Node 24).
- npm.
- Windows x64 for the authoritative NSIS build and installation smoke test.

## Install dependencies

From the repository root:

```sh
npm ci
npm ci --prefix orbita-agent/server
```

## Run validation

```sh
npm run check
npm test
npm audit --audit-level=high
npm --prefix orbita-agent/server audit --audit-level=high
```

The dependency audit blocks high and critical advisories. Lower severity advisories remain visible in the log and must be reviewed; they are not silently treated as absent.

## Build the Windows installer

Run on Windows x64:

```sh
npm run dist:win
```

The command uses electron-builder with NSIS and `--publish never`; it builds locally without creating a GitHub Release. The installer is written to:

`release/ORBITA-Universal-Plugin-Setup-x64.exe`

Linux builds are not authoritative for this Windows installer. The release workflow uses `windows-latest`, performs a clean install/startup/MCP/uninstall smoke test, and uploads the EXE separately from validation evidence.

See [RELEASE.md](./RELEASE.md) for publication.
