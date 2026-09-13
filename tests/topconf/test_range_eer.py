import pytest

from audiobookbench.topconf.evaluation.range_eer import RangeEERNotReady, range_eer


def test_range_eer_is_gated_until_reference_verification():
    with pytest.raises(RangeEERNotReady):
        range_eer([], [])
