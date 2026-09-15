[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,
    [int]$PartCount = 8,
    [string]$Url = 'https://openslr.trmal.net/resources/33/data_aishell.tgz',
    [Int64]$ContentLength = 15582913665
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($PartCount -lt 2) {
    throw 'PartCount must be at least 2.'
}

$partDir = Join-Path $OutputRoot 'data_aishell.parts'
if (!(Test-Path -LiteralPath $partDir)) {
    New-Item -ItemType Directory -Path $partDir | Out-Null
}

$existing = @(Get-ChildItem -LiteralPath $partDir -Filter 'part-*.bin' -File -ErrorAction SilentlyContinue)
if ($existing.Count -gt 0) {
    throw "Refusing to start over an existing parts directory: $partDir"
}

$partSize = [math]::Ceiling($ContentLength / $PartCount)
for ($index = 0; $index -lt $PartCount; $index++) {
    $start = [Int64]($index * $partSize)
    $end = [math]::Min($ContentLength - 1, [Int64](($index + 1) * $partSize - 1))
    $output = Join-Path $partDir ("part-{0:D2}.bin" -f $index)
    $errorLog = Join-Path $partDir ("part-{0:D2}.curl.log" -f $index)
    $argumentList = '-L --fail --retry 8 --retry-delay 5 --range "{0}-{1}" --output "{2}" --stderr "{3}" "{4}"' -f $start, $end, $output, $errorLog, $Url
    $process = Start-Process -FilePath 'curl.exe' -ArgumentList $argumentList -WindowStyle Hidden -PassThru
    Write-Output "started part=$index pid=$($process.Id) range=$start-$end output=$output"
}
