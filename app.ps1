Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Only hide the powershell console for *main* window, not the installer
if ($host.Name -eq 'ConsoleHost') {
    $consoleWindow = Get-Process -Id $PID | Where-Object {$_.MainWindowHandle -ne 0}
    if ($consoleWindow) {
        $signature = @"
[DllImport("user32.dll")]
public static extern bool ShowWindow(int hWnd, int nCmdShow);
"@
        Add-Type -Name Win32ShowWindowAsync -Namespace Win32Functions -MemberDefinition $signature
        $null = [Win32Functions.Win32ShowWindowAsync]::ShowWindow($consoleWindow.MainWindowHandle, 0)
    }
}

# Create the form
$form = New-Object System.Windows.Forms.Form
$form.Text = "MoH Nurses WFP Tool"
$form.Size = New-Object System.Drawing.Size(300,300)  # Slightly larger for a third section
$form.StartPosition = "CenterScreen"

# Prevent window resizing (block maximize, resizing, remove size grip)
$form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedDialog
$form.MaximizeBox = $false
$form.MinimizeBox = $true
$form.ShowInTaskbar = $true

# Create a bold font for labels
$boldFont = New-Object System.Drawing.Font("Microsoft Sans Serif",10,[System.Drawing.FontStyle]::Bold)

# Create the first label (bold and closer to button)
$label1 = New-Object System.Windows.Forms.Label
$label1.Text = "Install Requirements (One Time)"
$label1.Font = $boldFont
$label1.AutoSize = $true
$label1.Location = New-Object System.Drawing.Point(25,25)
$form.Controls.Add($label1)

# Create the Install button (put closer to label)
$buttonInstall = New-Object System.Windows.Forms.Button
$buttonInstall.Text = "Install"
$buttonInstall.Size = New-Object System.Drawing.Size(250,30)
$buttonInstall.Location = New-Object System.Drawing.Point(20,55)

# NOTE: Allow the console window to show for the install/setup script
$buttonInstall.Add_Click({
    try {
        $scriptPath = Join-Path -Path (Split-Path -Parent $PSCommandPath) -ChildPath "scripts\setup.ps1"
        if (Test-Path $scriptPath) {
            # Show the PowerShell window for the installer, do NOT use -WindowStyle Hidden!
            Start-Process powershell -WindowStyle Normal -ArgumentList "-NoProfile", "-ExecutionPolicy", "ByPass", "-File", "`"$scriptPath`""
            [System.Windows.Forms.MessageBox]::Show("Setup script launched. Please follow any prompts that appear in the new window.")
        }
        else {
            [System.Windows.Forms.MessageBox]::Show("Could not find setup.ps1 script in the scripts folder.", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        }
    } catch {
        [System.Windows.Forms.MessageBox]::Show("An error occurred while trying to launch the setup script.`n$_", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    }
})

$form.Controls.Add($buttonInstall)

# --- New section: Open Input Excel File ---

# Create label for Excel input
$labelInput = New-Object System.Windows.Forms.Label
$labelInput.Text = "Edit Model Input"
$labelInput.Font = $boldFont
$labelInput.AutoSize = $true
$labelInput.Location = New-Object System.Drawing.Point(25,100)
$form.Controls.Add($labelInput)

# Create the Open Excel button
$buttonOpenExcel = New-Object System.Windows.Forms.Button
$buttonOpenExcel.Text = "Open Input File"
$buttonOpenExcel.Size = New-Object System.Drawing.Size(250,30)
$buttonOpenExcel.Location = New-Object System.Drawing.Point(20,130)

# Open the Excel file when button is clicked
$buttonOpenExcel.Add_Click({
    try {
        $inputPath = Join-Path -Path (Split-Path -Parent $PSCommandPath) -ChildPath "data\MoH_Model_Input.xlsx"
        if (Test-Path $inputPath) {
            Start-Process $inputPath
        }
        else {
            [System.Windows.Forms.MessageBox]::Show("Could not find MoH_Model_Input.xlsx in the data folder.", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        }
    } catch {
        [System.Windows.Forms.MessageBox]::Show("An error occurred while trying to open the input excel file.`n$_", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    }
})

$form.Controls.Add($buttonOpenExcel)

# --- End new section ---

# Create the second label (bold and closer to button)
$label2 = New-Object System.Windows.Forms.Label
$label2.Text = "Calculate Supply / Demand / Gap"
$label2.Font = $boldFont
$label2.AutoSize = $true
$label2.Location = New-Object System.Drawing.Point(25,175)
$form.Controls.Add($label2)

# Create the Run Tool button (put closer to label)
$buttonRunTool = New-Object System.Windows.Forms.Button
$buttonRunTool.Text = "Run Tool"
$buttonRunTool.Size = New-Object System.Drawing.Size(250,30)
$buttonRunTool.Location = New-Object System.Drawing.Point(20,205)

# Define what happens on Run Tool click
$buttonRunTool.Add_Click({
    try {
        $scriptPath = Join-Path -Path (Split-Path -Parent $PSCommandPath) -ChildPath "scripts\run.ps1"
        if (Test-Path $scriptPath) {
            # Run the main tool script, showing the PowerShell window
            Start-Process powershell -WindowStyle Normal -ArgumentList "-NoProfile", "-ExecutionPolicy", "ByPass", "-File", "`"$scriptPath`"" -Wait

            # Show a final completion message
            [System.Windows.Forms.MessageBox]::Show("Tool Run Complete. Opening results file...", "Success", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)

            # Try to open the results Excel file inside ../output/spreadsheets
            $outputExcelPath = Join-Path -Path (Split-Path -Parent $PSCommandPath) -ChildPath "output\spreadsheets\MoH_Nurses_WFP_Tool_Output.xlsx"
            if (Test-Path $outputExcelPath) {
                Start-Process $outputExcelPath
            } else {
                [System.Windows.Forms.MessageBox]::Show("Could not find MoH_Nurses_WFP_Tool_Output.xlsx in output\spreadsheets.", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
            }
        }
        else {
            [System.Windows.Forms.MessageBox]::Show("Could not find run.ps1 script in the scripts folder.", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        }
    } catch {
        [System.Windows.Forms.MessageBox]::Show("An error occurred while trying to launch the run script or open the results file.`n$_", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    }
})

$form.Controls.Add($buttonRunTool)

[void]$form.ShowDialog()
