import pytest

from audiobookbench.topconf.schemas import Interval
from audiobookbench.topconf.evaluation.boundary import boundary_errors, false_positive_duration_per_hour
from audiobookbench.topconf.evaluation.event_localization import event_metrics, iou, match_events
from audiobookbench.topconf.evaluation.frame_localization import evaluate_frames, frame_labels


def test_perfect_and_shifted_intervals():
    truth = Interval(10, 20)
    assert iou(truth, truth) == 1.0
    assert boundary_errors(Interval(12, 22), truth) == {"onset_error_sec": 2.0, "offset_error_sec": 2.0}


def test_fragmented_and_duplicate_predictions_are_one_to_one():
    truth = (Interval(10, 20),)
    pred = [(Interval(10, 13), 0.9), (Interval(15, 20), 0.8), (Interval(10, 20), 0.7)]
    assert match_events(pred, truth, 0.5) == (1, 2, 0)
    assert event_metrics([(Interval(10, 20), 0.9)], truth)["map"] == 1.0


def test_empty_event_cases_are_explicit():
    assert event_metrics([], ())["map"] == 1.0
    assert event_metrics([], (Interval(1, 2),))["map"] == 0.0
    assert false_positive_duration_per_hour((Interval(0, 1),), (), 3600) == 1.0


def test_frame_support_alignment_is_explicit():
    supports = [(0, 1), (1, 2), (2, 3), (3, 4)]
    labels = frame_labels(supports, (Interval(1, 2),), overlap_threshold=0.5)
    assert labels.tolist() == [0, 1, 0, 0]
    assert evaluate_frames(supports, [0.1, 0.9, 0.2, 0.1], (Interval(1, 2),))["auroc"] == 1.0

    with pytest.raises(ValueError):
        frame_labels([(0, 1), (0.5, 2)], (Interval(1, 2),))
