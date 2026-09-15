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

$partDir = Join-Path $OutputRoot 'data_aishell.parts'
$partSize = [math]::Ceiling($ContentLength / $PartCount)
for ($index = 0; $index -lt $PartCount; $index++) {
    $start = [Int64]($index * $partSize)
    $end = [math]::Min($ContentLength - 1, [Int64](($index + 1) * $partSize - 1))
    $part = Join-Path $partDir ("part-{0:D2}.bin" -f $index)
    if (!(Test-Path -LiteralPath $part)) {
        throw "Missing original part: $part"
    }
    $actual = [Int64](Get-Item -LiteralPath $part).Length
    $next = $start + $actual
    if ($next -gt ($end + 1)) {
        throw "Part is larger than its declared range: $part"
    }
    if ($next -eq ($end + 1)) {
        Write-Output "complete part=$index bytes=$actual"
        continue
    }
    $tail = Join-Path $partDir ("part-{0:D2}.tail" -f $index)
    if (Test-Path -LiteralPath $tail) {
        throw "Refusing to overwrite an existing tail: $tail"
    }
    $errorLog = Join-Path $partDir ("part-{0:D2}.resume.curl.log" -f $index)
    $argumentList = '-L --fail --retry 8 --retry-delay 5 --range "{0}-{1}" --output "{2}" --stderr "{3}" "{4}"' -f $next, $end, $tail, $errorLog, $Url
    $process = Start-Process -FilePath 'curl.exe' -ArgumentList $argumentList -WindowStyle Hidden -PassThru
    Write-Output "started part=$index pid=$($process.Id) range=$next-$end tail=$tail"
}
