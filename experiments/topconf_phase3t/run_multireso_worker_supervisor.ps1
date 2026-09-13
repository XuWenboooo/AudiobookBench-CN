$ErrorActionPreference = "Stop"
$workerRoot = "F:\项目\申请实验室  TTS项目\AudiobookBench-CN-phase3t-multireso-worker"
$python = "F:\项目\申请实验室  TTS项目\envs\topconf-phase3v-multireso-py310\Scripts\python.exe"
$namespace = Join-Path $workerRoot "results\topconf_phase3t\multireso_worker_02"
$manifest = Join-Path $namespace "MULTIRESO_PHASE3T_RAW_OUTPUT_MANIFEST_V1.json"
$log = Join-Path $namespace "worker_supervisor.log"

Set-Location -LiteralPath $workerRoot
while ($true) {
    $stamp = Get-Date -Format o
    Add-Content -LiteralPath $log -Value "SUPERVISOR_START $stamp"
    & $python -u -c "from experiments.topconf_phase3t.run_multireso_worker import main; raise SystemExit(main())" --batch-size 4 --resume --recover-stale-lock *>> $log
    $exitCode = $LASTEXITCODE
    if (Test-Path -LiteralPath $manifest) {
        $state = Get-Content -Raw -LiteralPath $manifest | ConvertFrom-Json
        if ($state.status -eq "COMPLETE" -and $state.terminal -eq $state.planned) {
            Add-Content -LiteralPath $log -Value "SUPERVISOR_COMPLETE $(Get-Date -Format o)"
            exit 0
        }
    }
    Add-Content -LiteralPath $log -Value "SUPERVISOR_CHILD_EXIT code=$exitCode time=$(Get-Date -Format o); resuming same namespace"
    Start-Sleep -Seconds 2
}
