$ErrorActionPreference = "Stop"
python (Join-Path $PSScriptRoot "reproduce.py") --full
if ($LASTEXITCODE -ne 0) {
    throw "Cross-platform reproduction driver failed with exit code $LASTEXITCODE"
}
