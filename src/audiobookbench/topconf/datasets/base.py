from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class AdapterStatus(str, Enum):
    SKELETON = "SKELETON"
    BLOCKED_GT_UNAVAILABLE = "BLOCKED_GT_UNAVAILABLE"


@dataclass(frozen=True)
class DatasetAdapter:
    dataset_id: str
    official_source: str = "TBD_BEFORE_AUTHORIZATION"
    license: str = "TBD_BEFORE_AUTHORIZATION"
    split_policy: str = "TBD_BEFORE_AUTHORIZATION"
    audio_location: str = "TBD_BEFORE_AUTHORIZATION"
    gt_format: str = "TBD_BEFORE_AUTHORIZATION"
    speaker_metadata: str = "TBD_BEFORE_AUTHORIZATION"
    mechanism_metadata: str = "TBD_BEFORE_AUTHORIZATION"
    temporal_resolution: str = "TBD_BEFORE_AUTHORIZATION"
    conversion_policy: str = "No conversion authorized"
    known_limitations: str = "TBD_BEFORE_AUTHORIZATION"

    @property
    def status(self) -> AdapterStatus:
        return AdapterStatus.SKELETON

    def describe(self) -> dict[str, Any]:
        return {"dataset_id": self.dataset_id, "official_source": self.official_source, "license": self.license, "split_policy": self.split_policy, "audio_location": self.audio_location, "gt_format": self.gt_format, "speaker_metadata": self.speaker_metadata, "mechanism_metadata": self.mechanism_metadata, "temporal_resolution": self.temporal_resolution, "conversion_policy": self.conversion_policy, "known_limitations": self.known_limitations, "status": self.status.value}

    def load_ground_truth(self, *_args, **_kwargs):
        raise RuntimeError("GT unavailable: adapter is metadata-only and cannot infer or fabricate annotations")


class PartialSpoofAdapter(DatasetAdapter):
    def __init__(self) -> None:
        super().__init__("PartialSpoof")


class PartialEditAdapter(DatasetAdapter):
    def __init__(self) -> None:
        super().__init__("PartialEdit")
