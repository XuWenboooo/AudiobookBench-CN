import numpy as np
import pytest

from audiobookbench.topconf.evaluation.detection import auprc, auroc, eer, pool_localization


def test_detection_reference_fixture_is_perfect():
    y, s = [0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]
    assert auroc(y, s) == 1.0
    assert auprc(y, s) == 1.0
    assert eer(y, s) == 0.0


def test_detection_rejects_nan_and_one_class():
    with pytest.raises(ValueError):
        auroc([0, 1], [np.nan, 0.5])
    with pytest.raises(ValueError):
        auroc([1, 1], [0.1, 0.2])


def test_pooling_is_configurable_not_selected_by_results():
    assert pool_localization([0.1, 0.9], "max_pool") == 0.9
    assert pool_localization([0.1, 0.9], "mean_pool") == 0.5
    assert pool_localization([0.1, 0.9], "top_k_mean", top_k=1) == 0.9
