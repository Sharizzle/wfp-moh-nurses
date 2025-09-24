Set-Location ..

# Install uv if not already installed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv not found, installing..."
    pip install uv
} else {
    Write-Host "uv is already installed."
}

# Sync dependencies (must run in project root where pyproject.toml or requirements.txt exists)
Write-Host "Syncing dependencies..."
uv sync