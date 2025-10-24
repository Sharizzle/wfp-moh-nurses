# This code makes sense for running a Python app with a venv in PowerShell.

# Move up to project root
Set-Location (Join-Path $PSScriptRoot "..")

# Set venv directory name
$VenvDir = ".venv"

# Activate the virtual environment (PowerShell)
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
. $ActivateScript

# Print a message before running the tool
Write-Host "Tool is running, it will take a few seconds..."

# Run the app.py script
python app.py