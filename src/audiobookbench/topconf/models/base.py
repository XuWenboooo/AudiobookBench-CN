from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Provenance:
    model_id: str
    repository: str = "TBD_BEFORE_AUTHORIZATION"
    commit: str = "TBD_BEFORE_AUTHORIZATION"
    checkpoint_hash: str = "TBD_BEFORE_AUTHORIZATION"
    license: str = "TBD_BEFORE_AUTHORIZATION"
    dataset: str = "TBD_BEFORE_AUTHORIZATION"


class DetectorAdapter:
    def __init__(self, provenance: Provenance) -> None:
        self.provenance = provenance

    def predict_utterance_score(self, audio: Any) -> float:
        raise NotImplementedError("Whether-B adapter interface only; no model execution in Phase 2")


class LocalizerAdapter:
    def __init__(self, provenance: Provenance) -> None:
        self.provenance = provenance

    def predict(self, audio: Any):
        raise NotImplementedError("localizer adapter interface only; no model execution in Phase 2")
