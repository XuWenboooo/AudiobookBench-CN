import hashlib, json
from pathlib import Path
import pytest
from audiobookbench.week5.exp1 import guard_path
from audiobookbench.week5.exp2 import FEATURES as E2_FEATURES
from audiobookbench.week5.exp3 import FOLDS, INPUT, load_population

def test_exp2_population_identity():
    a=Path('data/manifests/week5_exp2_qualification_population.json').read_bytes()
    b=Path('data/manifests/week5_exp3_qualification_population.json').read_bytes()
    assert hashlib.sha256(a).hexdigest()==hashlib.sha256(b).hexdigest()

def test_ood_separation_and_fold_exclusion():
    for allowed,ood in FOLDS.values():
        assert ood not in allowed
        assert set(allowed)|{ood}=={'controlled_splice','F5','CosyVoice2'}

def test_week4_guard_and_inference_policy():
    with pytest.raises(RuntimeError): guard_path('results/week4_adaptive_redteam_runs/held_out/score.json')
    assert 'generator' not in [x.lower() for x in INPUT]

def test_exp2_b4_contract_is_reused():
    assert INPUT==E2_FEATURES['B4_FULL']

def test_training_constants_are_deterministic():
    assert FOLDS=={"fold_a":(["controlled_splice","F5"],"CosyVoice2"),"fold_b":(["controlled_splice","CosyVoice2"],"F5"),"fold_c":(["F5","CosyVoice2"],"controlled_splice")}
