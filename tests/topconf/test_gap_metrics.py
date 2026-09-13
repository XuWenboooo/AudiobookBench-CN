from audiobookbench.topconf.evaluation.gap_metrics import ld_at_dr95
from audiobookbench.topconf.evaluation.robustness import build_point


def test_ld_dr95_is_estimable_and_not_cross_scale_subtraction():
    points = [build_point(0, 0.9, 0.8, clean_detection=0.9, clean_localization=0.8), build_point(1, 0.86, 0.4, clean_detection=0.9, clean_localization=0.8)]
    result = ld_at_dr95(points)
    assert result["status"] == "ESTIMABLE"
    assert result["ld_at_dr95"] == 0.25


def test_empty_feasible_set_is_not_estimable():
    point = build_point(1, 0.5, 0.4, clean_detection=0.9, clean_localization=0.8)
    assert ld_at_dr95([point])["status"] == "NOT_ESTIMABLE"
