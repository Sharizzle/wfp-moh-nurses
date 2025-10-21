# Stop on first error
$ErrorActionPreference = "Stop"

# Move up to project root
Set-Location (Join-Path $PSScriptRoot "..")

# Set venv directory name
$VenvDir = ".venv"

# Create virtual environment if it does not exist
if (-not (Test-Path $VenvDir -PathType Container)) {
    Write-Host "Creating virtual environment in $VenvDir..."
    python -m venv $VenvDir
}

# Activate the virtual environment
# (dot sourcing works in PowerShell)
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
. $ActivateScript

# Upgrade pip within the venv
python -m pip install --upgrade pip

# Install dependencies if requirements.txt exists
if (Test-Path "requirements.txt") {
    Write-Host "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
} elseif (Test-Path "pyproject.toml") {
    Write-Host "Installing dependencies from pyproject.toml using pip..."
    pip install .
} else {
    Write-Host "No requirements.txt or pyproject.toml found, skipping dependency installation."
}