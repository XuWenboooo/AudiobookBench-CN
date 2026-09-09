from audiobookbench.evaluation.metrics import binary_f1, interval_iou


def test_binary_f1():
    assert abs(binary_f1([1, 0, 1], [1, 0, 0]) - 2/3) < 1e-9


def test_interval_iou():
    assert abs(interval_iou(0, 2, 1, 3) - 1/3) < 1e-9
