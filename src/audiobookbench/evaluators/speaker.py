from __future__ import annotations

from abc import ABC, abstractmethod
import numpy as np

class SpeakerEvaluator(ABC):
    name: str = "abstract"

    @abstractmethod
    def embed(self, audio: np.ndarray, sr: int) -> np.ndarray:
        raise NotImplementedError

class NotConfiguredSpeakerEvaluator(SpeakerEvaluator):
    name = "not_configured"

    def embed(self, audio: np.ndarray, sr: int) -> np.ndarray:
        raise RuntimeError(
            "No real speaker embedding backend configured. Add ECAPA/WavLM/etc. before formal speaker claims."
        )


def cosine_similarity(a: np.ndarray, b: np.ndarray, eps: float = 1e-8) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + eps
    return float(np.dot(a, b) / denom)


def speaker_representation_distance(reference: np.ndarray, current: np.ndarray) -> float:
    return 1.0 - cosine_similarity(reference, current)
