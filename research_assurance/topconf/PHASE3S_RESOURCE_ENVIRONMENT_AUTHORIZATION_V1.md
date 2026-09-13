# Phase 3S Resource and Environment Recovery Authorization v1

Status: **AUTHORIZED FOR ISOLATED INFRASTRUCTURE RECOVERY / NOT SCIENTIFIC REPRODUCTION**

This is a new append-only Phase 3S authorization. It does not modify the
original Phase 3 or Phase 3R closure, and it does not authorize Phase 4,
RQ1/RQ2/RQ3, metric computation, model ranking, or confirmatory analysis.

```text
PHASE3S_AUTHORIZATION_ID = P3S-2026-09-13-01
BASE_COMMIT = 115776176c5ba55310610a5738da6ce8bef8b729
ORIGINAL_PHASE3_CLOSURE = BLOCKED
PHASE3R_CLOSURE = BLOCKED

AUTHORIZED_ENVIRONMENT_CHANGES = external isolated venv only; no system Python or primary venv changes
AUTHORIZED_PYTHON_VERSIONS = Python 3.10.11 from F:\\项目\\申请实验室\\python.exe; no system downgrade
AUTHORIZED_CUDA_TESTS = torch import, CUDA availability, GPU identity, CUDA tensor allocation, small matmul, fairseq import, verified XLSR load
AUTHORIZED_FAIRSEQ_SOURCE = local official-source cache fairseq-a54021305d6b3c4c5959ac9395135f63202db8f1
AUTHORIZED_FAIRSEQ_COMMIT = a54021305d6b3c4c5959ac9395135f63202db8f1 (archive SHA256 D70577F2D00E066C2EF14F6519623B90FFACB94E07C56F5406BA425C2BF8A85A)
AUTHORIZED_RUNTIME_TARGET = Python 3.10.11 + PyTorch 2.2.2/cu121 candidate + legacy fairseq source; exact installed manifest must be recorded before any smoke
AUTHORIZED_DOWNLOAD_TRANSPORTS = curl HTTP/1.1 complete transfer and one curl HTTP Range/resume transfer, each bounded and logged
AUTHORIZED_OFFICIAL_SOURCES = PartialEdit Zenodo 18829689; PartialSpoof Zenodo 5766198 and official repo; MultiReso Zenodo 6674660 and frozen official repo; existing verified CFPRF artifacts; official LlamaPartialSpoof repository/Zenodo only
DOWNLOAD_BUDGET = PartialEdit E1 one complete curl transport plus one resume attempt; MultiReso checkpoint one bounded curl transport; no repetition of Phase3R request sequence
AUTHORIZED_SMOKE_SCOPE = environment-only CUDA/fairseq/XLSR load; after full-audio parser PASS, at most 1-3 authorized CFPRF samples; no metric or ranking
AUTHORIZED_DATASETS = PartialEdit v1.1 E1 first; PartialSpoof v1.2 transport feasibility only; LlamaPartialSpoof audio only through a new author-controlled official path
AUTHORIZED_MODELS = existing verified CFPRF checkpoints; official PartialSpoof MultiReso checkpoint only after provenance/hash verification; SAL/BAM only after their gates pass
AUTHORIZED_OUTPUT_NAMESPACE = results/topconf/reproduction_recovery/<dataset>/<baseline>/<phase3s_invocation_id>

RIGHTS_POLICY = official source and license/provenance required; no unresolved-rights artifact may be used or redistributed
PRIMARY_ENVIRONMENT_POLICY = existing Python 3.12/CUDA environment is read-only and must remain unchanged
STORAGE_POLICY = audit free space before any multi-GB archive; no download if expected archive plus extraction headroom is unsafe
FAILURE_ACCOUNTING = log source, file identity, method, transport, start/end, HTTP status, bytes, expected size, checksum, and failure category
RETRY_POLICY = bounded infrastructure recovery only; no outcome/performance/seed/checkpoint shopping
SUBSTITUTION_POLICY = availability, provenance, rights, and hardware only; RESULT_BASED_SUBSTITUTIONS = 0

PROHIBITED_ACTIONS = Phase 4; RQ1/RQ2/RQ3; full benchmark; metric computation; model ranking; training/retraining; GT edits; unofficial mirrors; paid compute; forced CPU full reproduction; modification of the primary environment; modification of historical closures
REAUTHORIZATION_REQUIRED_FOR = new dataset, new checkpoint, new model, new output contract, new adapter/evaluator, any full reproduction, or any transport beyond the frozen budget
HUMAN_REVIEW_REQUIRED_BEFORE_PHASE4 = YES
```

The authorization is frozen before any new model inference. Resource
materialization, if successful, remains infrastructure/reproduction evidence;
it cannot by itself change the original Phase 3 or Phase 3R conclusion.
