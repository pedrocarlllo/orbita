$ErrorActionPreference = "Continue"

function Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "============================================================"
    Write-Host $Title
    Write-Host "============================================================"
}

function Run-ReadOnlyCommand {
    param([string]$Label, [scriptblock]$Command)
    Write-Host ""
    Write-Host "--- $Label ---"
    try {
        & $Command
        Write-Host "EXIT_CODE: $LASTEXITCODE"
    } catch {
        Write-Host "ERRO_LITERAL:"
        Write-Host $_.Exception.Message
    }
}

function Test-JsonFile {
    param([string]$Path)
    Write-Host ""
    Write-Host "--- JSON: $Path ---"
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Write-Host "AUSENTE"
        return
    }
    $raw = Get-Content -LiteralPath $Path -Raw
    Write-Host "CONTEUDO_LITERAL:"
    Write-Host $raw
    try {
        $null = $raw | ConvertFrom-Json -ErrorAction Stop
        Write-Host "JSON_VALIDO: SIM"
    } catch {
        Write-Host "JSON_VALIDO: NAO"
        Write-Host "ERRO_JSON_LITERAL:"
        Write-Host $_.Exception.Message
    }
}

function Test-JsFile {
    param([string]$Path)
    Write-Host ""
    Write-Host "--- NODE_CHECK: $Path ---"
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Write-Host "AUSENTE"
        return
    }
    & node --check "$Path" 2>&1
    Write-Host "EXIT_CODE: $LASTEXITCODE"
}

Section "OT-006 || INICIO"
Write-Host "DATA_HORA: $(Get-Date -Format o)"
Write-Host "USUARIO: $env:USERNAME"
Write-Host "COMPUTADOR: $env:COMPUTERNAME"
Write-Host "DIRETORIO_ATUAL: $(Get-Location)"
Write-Host "POWERSHELL_VERSION:"
$PSVersionTable | Format-List | Out-String | Write-Host

Section "1 | POLITICA DE EXECUCAO DO POWERSHELL"
Run-ReadOnlyCommand "Get-ExecutionPolicy -List" {
    Get-ExecutionPolicy -List
}

Section "2 | VERSOES DISPONIVEIS"
Run-ReadOnlyCommand "node --version" { node --version }
Run-ReadOnlyCommand "npm.cmd --version" { npm.cmd --version }
Run-ReadOnlyCommand "git --version" { git --version }

Section "3 | CAMINHOS DO ORBITA"
$SourceRoot = "C:\ORBITA-Universal-Plugin-Windows-0.1.0\orbita-agent"
$InstalledRoot = Join-Path $HOME "plugins\orbita-agent"
$MarketplacePath = Join-Path $HOME ".agents\plugins\marketplace.json"
$CodexConfigPath = Join-Path $HOME ".codex\config.toml"
$OrbitaDataDir = Join-Path $env:LOCALAPPDATA "ORBITA"

$Paths = [ordered]@{
    "SOURCE_ROOT" = $SourceRoot
    "INSTALLED_ROOT" = $InstalledRoot
    "MARKETPLACE" = $MarketplacePath
    "CODEX_CONFIG" = $CodexConfigPath
    "ORBITA_DATA_DIR" = $OrbitaDataDir
}

foreach ($key in $Paths.Keys) {
    $p = $Paths[$key]
    Write-Host "$key = $p"
    Write-Host "EXISTE: $(Test-Path -LiteralPath $p)"
}

Section "4 | ESTRUTURA BASICA DO PACOTE FONTE"
if (Test-Path -LiteralPath $SourceRoot -PathType Container) {
    Write-Host "Listando raiz do pacote fonte:"
    Get-ChildItem -LiteralPath $SourceRoot -Force | Select-Object Mode, Length, LastWriteTime, Name | Format-Table -AutoSize | Out-String | Write-Host
    Write-Host "Listando server/src:"
    $src = Join-Path $SourceRoot "server\src"
    if (Test-Path -LiteralPath $src) {
        Get-ChildItem -LiteralPath $src -Force | Select-Object Mode, Length, LastWriteTime, Name | Format-Table -AutoSize | Out-String | Write-Host
    } else {
        Write-Host "server/src AUSENTE"
    }
} else {
    Write-Host "SOURCE_ROOT AUSENTE"
}

Section "5 | ESTRUTURA BASICA DO PLUGIN INSTALADO"
if (Test-Path -LiteralPath $InstalledRoot -PathType Container) {
    Write-Host "Listando raiz do plugin instalado:"
    Get-ChildItem -LiteralPath $InstalledRoot -Force | Select-Object Mode, Length, LastWriteTime, Name | Format-Table -AutoSize | Out-String | Write-Host
    Write-Host "Listando server/src instalado:"
    $installedSrc = Join-Path $InstalledRoot "server\src"
    if (Test-Path -LiteralPath $installedSrc) {
        Get-ChildItem -LiteralPath $installedSrc -Force | Select-Object Mode, Length, LastWriteTime, Name | Format-Table -AutoSize | Out-String | Write-Host
    } else {
        Write-Host "server/src instalado AUSENTE"
    }
} else {
    Write-Host "INSTALLED_ROOT AUSENTE"
}

Section "6 | MANIFESTOS DO PACOTE FONTE"
Test-JsonFile (Join-Path $SourceRoot ".mcp.json")
Test-JsonFile (Join-Path $SourceRoot "mcp.json")
Test-JsonFile (Join-Path $SourceRoot "plugin.json")
Test-JsonFile (Join-Path $SourceRoot "server\package.json")

Section "7 | MANIFESTOS DO PLUGIN INSTALADO"
Test-JsonFile (Join-Path $InstalledRoot ".mcp.json")
Test-JsonFile (Join-Path $InstalledRoot "mcp.json")
Test-JsonFile (Join-Path $InstalledRoot "plugin.json")
Test-JsonFile (Join-Path $InstalledRoot "server\package.json")

Section "8 | DEPENDENCIAS"
foreach ($root in @($SourceRoot, $InstalledRoot)) {
    Write-Host ""
    Write-Host "--- Dependencias em: $root ---"
    $server = Join-Path $root "server"
    $nodeModules = Join-Path $server "node_modules"
    $lock = Join-Path $server "package-lock.json"
    $sdk = Join-Path $nodeModules "@modelcontextprotocol\server"
    $zod = Join-Path $nodeModules "zod"
    Write-Host "server existe: $(Test-Path -LiteralPath $server)"
    Write-Host "node_modules existe: $(Test-Path -LiteralPath $nodeModules)"
    Write-Host "package-lock.json existe: $(Test-Path -LiteralPath $lock)"
    Write-Host "@modelcontextprotocol/server existe: $(Test-Path -LiteralPath $sdk)"
    Write-Host "zod existe: $(Test-Path -LiteralPath $zod)"
}

Section "9 | VERIFICACAO DE SINTAXE"
foreach ($root in @($SourceRoot, $InstalledRoot)) {
    Write-Host ""
    Write-Host "--- node --check em: $root ---"
    Test-JsFile (Join-Path $root "server\src\index.mjs")
    Test-JsFile (Join-Path $root "server\src\tools.mjs")
    Test-JsFile (Join-Path $root "server\src\security.mjs")
    Test-JsFile (Join-Path $root "server\src\state.mjs")
    Test-JsFile (Join-Path $root "server\src\workspace.mjs")
    Test-JsFile (Join-Path $root "server\src\process.mjs")
    Test-JsFile (Join-Path $root "server\src\approvals.mjs")
    Test-JsFile (Join-Path $root "server\src\audit.mjs")
}

Section "10 | PADROES SUSPEITOS"
foreach ($root in @($SourceRoot, $InstalledRoot)) {
    Write-Host ""
    Write-Host "--- Procurando padroes suspeitos em: $root ---"
    $toolsPath = Join-Path $root "server\src\tools.mjs"
    $securityPath = Join-Path $root "server\src\security.mjs"
    $installPath = Join-Path $root "scripts\Install-ORBITA.ps1"
    if (Test-Path -LiteralPath $toolsPath) {
        Write-Host "tools.mjs:"
        Select-String -LiteralPath $toolsPath -Pattern 'runProces s|st aged|li mited|st ate|incl udes|l ength|Err or|str ing|mustExi st|bytes Before|= >' -SimpleMatch:$false
    } else {
        Write-Host "tools.mjs AUSENTE"
    }
    if (Test-Path -LiteralPath $securityPath) {
        Write-Host "security.mjs replaceAll:"
        Select-String -LiteralPath $securityPath -Pattern 'replaceAll'
    } else {
        Write-Host "security.mjs AUSENTE"
    }
    if (Test-Path -LiteralPath $installPath) {
        Write-Host "Install-ORBITA.ps1 linhas suspeitas:"
        Select-String -LiteralPath $installPath -Pattern '\$\.Name|\$\.FullName|^Atualiza somente|^A política' -SimpleMatch:$false
    } else {
        Write-Host "Install-ORBITA.ps1 AUSENTE"
    }
}

Section "11 | MARKETPLACE E CODEX CONFIG"
if (Test-Path -LiteralPath $MarketplacePath -PathType Leaf) {
    Write-Host "Marketplace existe: SIM"
    try {
        $marketRaw = Get-Content -LiteralPath $MarketplacePath -Raw
        $market = $marketRaw | ConvertFrom-Json -ErrorAction Stop
        Write-Host "Marketplace JSON valido: SIM"
        $orbitaEntries = @($market.plugins | Where-Object { $_.name -eq "orbita-agent" })
        Write-Host "Entradas orbita-agent: $($orbitaEntries.Count)"
        if ($orbitaEntries.Count -gt 0) {
            $orbitaEntries | ConvertTo-Json -Depth 10 | Write-Host
        }
    } catch {
        Write-Host "Marketplace JSON valido: NAO"
        Write-Host $_.Exception.Message
    }
} else {
    Write-Host "Marketplace existe: NAO"
}

if (Test-Path -LiteralPath $CodexConfigPath -PathType Leaf) {
    Write-Host "Codex config existe: SIM"
    $codexRaw = Get-Content -LiteralPath $CodexConfigPath -Raw
    Write-Host "Contem texto orbita-agent: $($codexRaw.Contains('orbita-agent'))"
    Write-Host "Contem texto orbita-local: $($codexRaw.Contains('orbita-local'))"
} else {
    Write-Host "Codex config existe: NAO"
}

Section "12 | DADOS ORBITA"
if (Test-Path -LiteralPath $OrbitaDataDir) {
    Write-Host "ORBITA_DATA_DIR existe: SIM"
    Get-ChildItem -LiteralPath $OrbitaDataDir -Force | Select-Object Mode, Length, LastWriteTime, Name | Format-Table -AutoSize | Out-String | Write-Host
} else {
    Write-Host "ORBITA_DATA_DIR existe: NAO"
}

Section "OT-006 || FIM"
Write-Host ""
Write-Host "INSTRUCAO AO AGENTE:"
Write-Host "Retorne a saida literal completa desta execucao."
Write-Host "Nao altere nada."
Write-Host "Nao execute instalador."
Write-Host "Nao execute npm install."
Write-Host "Nao inicie o servidor MCP ainda."
Write-Host "A proxima ordem sera emitida somente da analise desta saida."
