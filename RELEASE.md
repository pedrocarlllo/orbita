# GitHub Release guide

ORBITA publishes the Windows x64 installer through a tag-driven GitHub Actions workflow.

## Prepare a version

1. Review and merge the release candidate into `main`.
2. Update `version` in `package.json` and the matching root `package-lock.json` package metadata.
3. Add the user-visible changes to [CHANGELOG.md](./CHANGELOG.md).
4. Run `npm test`, `npm run check`, and both dependency audits from [BUILD.md](./BUILD.md).
5. Confirm the current security review has no unresolved release-blocking finding.

Use SemVer: `MAJOR.MINOR.PATCH`. Pre-release identifiers such as `0.1.0-rc.1` are published as GitHub pre-releases when the tag and package version match exactly.

## Trigger publication

Create and push an annotated tag matching the package version:

```sh
git tag -a v0.1.0 -m "ORBITA Universal Plugin v0.1.0"
git push origin v0.1.0
```

The tag triggers `.github/workflows/release-windows.yml`. The workflow:

1. Validates SemVer and exact equality with `package.json`.
2. Refuses to overwrite a Release already published for that tag.
3. Calls the reusable Windows build workflow.
4. Runs dependency audit, checks, tests, NSIS build, standard-user installation, app/MCP smoke, uninstallation, and user-data preservation.
5. Requires `releaseReady=true`, successful workflow steps, a Windows x64 runtime, a valid PE installer, and a matching SHA-256.
6. Creates the GitHub Release and attaches only `ORBITA-Universal-Plugin-Setup-x64.exe`.

The publish job alone receives `contents: write` and uses the repository-provided `GITHUB_TOKEN`; no personal access token is stored in source code. The build/validation jobs remain read-only.

## Where to download

Open the repository's **Releases** page. The installer appears under **Assets**. GitHub-generated Source code ZIP/TAR.GZ files are source snapshots, not application installers.

The Actions validation ZIP is evidence/log output, not the distributable installer.

## Integrity and limitations

Verify the SHA-256 shown in the Release notes against the downloaded EXE. The current installer is unsigned; Windows may show a publisher warning. The CI smoke test verifies the installed desktop app and packaged MCP server, but it cannot verify a connection to ChatGPT Desktop official host. That limitation remains explicit and must not be represented as a completed host integration test.

Do not reuse or move a published tag. Publish a new SemVer patch version to correct an existing release.
