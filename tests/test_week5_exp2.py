import numpy as np
import pytest
from audiobookbench.week5.exp1 import guard_path
from audiobookbench.week5.exp2 import _scale_features, FEATURES, SCALES, prepare

def test_multiscale_alignment_and_determinism():
    a=_scale_features([.1,.4,.2,.3]); b=_scale_features([.1,.4,.2,.3])
    assert a==b
    assert len(a)==4 and a[0]['short_score_center']==a[0]['medium_score_center']==a[0]['long_score_center']

def test_edge_padding_is_nan():
    x=_scale_features([.1,.2])
    assert np.isnan(x[0]['short_left_context_mean'])
    assert np.isnan(x[0]['long_left_context_mean'])

def test_feature_manifest_and_no_gt_fields():
    assert set(SCALES)=={'SHORT','MEDIUM','LONG'}
    assert 'B3_MS' in FEATURES and 'B4_FULL' in FEATURES
    assert all(not any(t in f.lower() for t in ('label','region','attack','gt')) for fs in FEATURES.values() for f in fs)

def test_capacity_control_is_deterministic_and_same_dimension():
    assert len(FEATURES['B2_CAPACITY_MATCHED_CONTROL'])==len(FEATURES['B4_FULL'])
    assert FEATURES['B2_CAPACITY_MATCHED_CONTROL']==FEATURES['B2_CAPACITY_MATCHED_CONTROL']

def test_generator_ood_folds_are_separated():
    folds={'a':({'controlled_splice','F5'},'CosyVoice2'),'b':({'controlled_splice','CosyVoice2'},'F5'),'c':({'F5','CosyVoice2'},'controlled_splice')}
    for train,ood in folds.values(): assert ood not in train

def test_exp2_week4_guard():
    with pytest.raises(RuntimeError): guard_path('results/week4_adaptive_redteam_runs/week4_validation_x/metrics.json')
