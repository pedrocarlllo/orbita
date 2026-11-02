# Changelog

All notable changes to ORBITA Universal Plugin are recorded here.

The project has not published a stable GitHub Release yet.

## [Unreleased]

### Added
- Electron desktop manager for local ORBITA configuration and workspace authorization.
- Local MCP STDIO server with eleven registered tools.
- Windows x64 NSIS installer build and smoke-test workflow.
- SemVer-based GitHub Release pipeline with installer SHA-256 verification.

### Security and validation
- Workspace file access is scoped to the selected project directory.
- File changes use preview tokens, base-hash verification, backup, and atomic replacement.
- Installer Release publication is gated by Windows checks, dependency audit, build, smoke results, and artifact hash verification.

### Known limitations
- The installer is not digitally signed.
- ChatGPT Desktop official-host integration is not verified by the GitHub Actions runner.
- Repair and in-place update flows are not included in the current smoke test.
