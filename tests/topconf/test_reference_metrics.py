from sklearn.metrics import average_precision_score, roc_auc_score

from audiobookbench.topconf.evaluation.detection import auprc, auroc
from audiobookbench.topconf.evaluation.event_localization import iou
from audiobookbench.topconf.schemas import Interval


def test_detection_matches_sklearn_reference_on_synthetic_fixture():
    labels = [0, 1, 0, 1, 1]
    scores = [0.1, 0.8, 0.2, 0.7, 0.4]
    assert auroc(labels, scores) == roc_auc_score(labels, scores)
    assert auprc(labels, scores) == average_precision_score(labels, scores)


def test_interval_iou_reference_fixture():
    assert iou(Interval(0, 2), Interval(1, 3)) == 1 / 3
