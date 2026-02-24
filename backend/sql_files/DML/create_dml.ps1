    
    # Citation for use of AI Tools:
    # Date: 02/23/2026
    # Prompts used to generate PowerShell script
    # Write a PowerShell script called create_dml that combines read, create, update, and delete SQL files
    # into one DML.sql file in a Submission folder.
    # Update the script to use read.sql, create.sql, update.sql, and delete.sql.
    # AI Source URL: https://chat.openai.com/
    








# Powershell script that combines the four DML sql files (CREATE,READ,UPDATE,DELETE)


param(
    [string]$OutputFile = "DML.sql"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$outputPath = Join-Path (Join-Path $scriptDir "Submission") $OutputFile

$sqlFiles = @(
    "create.sql",
    "read.sql",
    "update.sql",
    "delete.sql"
)

$combined = foreach ($file in $sqlFiles) {
    $filePath = Join-Path $scriptDir $file
    "-- $file`r`n" + (Get-Content -Raw -Path $filePath).TrimEnd()
}

[System.IO.File]::WriteAllText(
    $outputPath,
    (($combined -join "`r`n`r`n") + "`r`n"),
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host "Created $outputPath"
