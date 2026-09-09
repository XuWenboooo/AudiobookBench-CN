import numpy as np
from audiobookbench.security.manipulation import replace_segment, segment_labels


def test_replace_segment_keeps_length_and_interval():
    sr = 10
    src = np.zeros(100, dtype=np.float32)
    repl = np.ones(50, dtype=np.float32)
    out, rec = replace_segment(src, repl, sr, 2.0, 4.0)
    assert len(out) == len(src)
    assert out[:20].sum() == 0
    assert out[20:40].sum() == 20
    assert out[40:].sum() == 0
    assert rec.attack_start == 2.0
    assert rec.attack_end == 4.0


def test_segment_labels_overlap():
    starts = np.array([0, 1, 2, 3, 4], dtype=float)
    ends = starts + 1
    y = segment_labels(starts, ends, 1.5, 3.2)
    assert y.tolist() == [0, 1, 1, 1, 0]
