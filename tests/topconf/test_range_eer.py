from audiobookbench.topconf.evaluation.range_eer import range_eer, range_rates
from audiobookbench.topconf.schemas import Interval


def test_range_eer_synthetic_reference_cases():
    supports = [(0, 1), (1, 2), (2, 3), (3, 4)]
    truth = (Interval(1, 2), Interval(3, 4))
    perfect = range_eer(supports, [0.0, 1.0, 0.0, 1.0], truth)
    assert perfect["eer"] == 0.0
    miss = range_eer(supports, [0.0, 0.0, 0.0, 0.0], truth)
    assert miss["eer"] == 0.5


def test_range_eer_resolution_and_constant_scores_are_explicit():
    truth = (Interval(1, 3),)
    result = range_eer([(0, 2), (2, 4)], [0.2, 0.8], truth)
    assert result["status"] == "ESTIMABLE"


def test_range_rates_matches_independent_published_equation_oracle():
    supports = [(0, 1), (1, 2), (2, 3), (3, 4)]
    scores = [0.2, 0.9, 0.1, 0.8]
    truth = (Interval(1, 2), Interval(3, 4))
    fpr, fnr = range_rates(supports, scores, truth, 0.5)
    # Eq. (5)/(6): duration of spoof-positive overlap with bona fide and
    # spoof-negative overlap with spoof, normalized by N and P duration.
    assert (fpr, fnr) == (0.0, 0.0)
