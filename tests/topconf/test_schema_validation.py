import pytest

from audiobookbench.topconf.schemas import Interval, PredictionRecord, SchemaValidationError, validate_unique_case_ids


def record(**kwargs):
    base = dict(case_id="c1", dataset_id="toy", split_id="dev", mechanism_id="m1", audio_duration_sec=30.0, ground_truth_intervals=(Interval(10, 20),))
    base.update(kwargs)
    return PredictionRecord(**base)


def test_prediction_contract_allows_optional_outputs_absent():
    assert record().case_id == "c1"


@pytest.mark.parametrize("kwargs", [dict(audio_duration_sec=float("nan")), dict(frame_times_sec_optional=((0, 1), (0.5, 2)), frame_scores_optional=(0.1, 0.2)), dict(ground_truth_intervals=(Interval(29, 31),))])
def test_contract_fails_closed(kwargs):
    with pytest.raises(SchemaValidationError):
        record(**kwargs)


def test_duplicate_ids_fail_closed():
    with pytest.raises(SchemaValidationError):
        validate_unique_case_ids([record(), record()])
