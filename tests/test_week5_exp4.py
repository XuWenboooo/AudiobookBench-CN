import hashlib, json
from pathlib import Path
import pytest
from audiobookbench.week5.exp1 import guard_path
from audiobookbench.week5.exp3 import FOLDS
from audiobookbench.week5.exp4 import SSL_DIR, _l2

def test_exp2_population_identity():
    a=Path('data/manifests/week5_exp2_qualification_population.json').read_bytes(); b=Path('data/manifests/week5_exp4_qualification_population.json').read_bytes()
    assert hashlib.sha256(a).hexdigest()==hashlib.sha256(b).hexdigest()

def test_temporal_contract_closed_and_fold_identity():
    c=Path('configs/week5_exp4_frozen_ssl_representation.yaml').read_text(encoding='utf-8')
    assert 'temporal_scale_search: CLOSED' in c
    assert FOLDS['fold_c'][1]=='controlled_splice'

def test_week4_guard_and_no_generator_inference():
    with pytest.raises(RuntimeError): guard_path('results/week4_adaptive_redteam_runs/week4_validation_01/score.json')
    r=Path('results/week5_exp4/representation_manifest.json')
    if r.exists(): assert json.loads(r.read_text())['E1']['frozen'] is True

def test_ssl_asset_identity_is_local():
    p=Path(SSL_DIR)/'pytorch_model.bin'; assert p.is_file(); assert p.stat().st_size>100_000_000

def test_l2_pooling_deterministic():
    import numpy as np
    x=np.asarray([[3.,4.],[0.,2.]])
    a=_l2(x); b=_l2(x); assert np.array_equal(a,b); assert np.allclose(np.linalg.norm(a,axis=1),1.0)
