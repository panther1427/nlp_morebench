$envFile = Join-Path $PSScriptRoot ".env"

if (-not (Test-Path -LiteralPath $envFile)) {
    throw "Missing .env file at $envFile"
}

Get-Content -LiteralPath $envFile | ForEach-Object {
    $line = $_.Trim()

    if (-not $line -or $line.StartsWith("#")) {
        return
    }

    $name, $value = $line -split "=", 2
    if (-not $value) {
        return
    }

    $name = $name.Trim()
    $value = $value.Trim().Trim('"').Trim("'")
    [Environment]::SetEnvironmentVariable($name, $value, "Process")
}

$requiredVariables = @("API_OPEN_ROUTER", "API_HUGGING_FACE", "MODEL")
foreach ($name in $requiredVariables) {
    if (-not [Environment]::GetEnvironmentVariable($name, "Process")) {
        throw "Missing required variable '$name' in .env"
    }
}

python (Join-Path $PSScriptRoot "run_inferences_on_dilemmas.py") `
    -ap openrouter `
    -ak $env:API_OPEN_ROUTER `
    -m $env:MODEL `
    -ht $env:API_HUGGING_FACE `
    -d
