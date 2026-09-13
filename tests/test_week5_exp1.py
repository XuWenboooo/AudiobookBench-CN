import numpy as np
import pytest
from audiobookbench.week5.exp1 import guard_path, temporal_features, region, prepare_manifest

def test_week4_guard_fail_closed():
    with pytest.raises(RuntimeError): guard_path("results/week4_validation/x.csv")
    with pytest.raises(RuntimeError): guard_path("results/foo/held_out.csv")
    guard_path("results/week5_exp1/metrics.json")

def test_regions_are_mutually_valid():
    vals=[region(100,300,150,250,100,150,0,50), region(100,300,150,250,100,150,150,250), region(100,300,150,250,100,150,300,350)]
    assert vals == ["clean", "core", "clean"]
    assert set(vals) <= {"clean","boundary","core"}

def test_features_do_not_accept_gt():
    f=temporal_features([.1,.4,.2])
    assert set(f[1]) == {"b1b_score","left_delta","right_delta","local_gradient","local_mean","local_std","local_max","local_min","boundary_contrast"}
    assert "label" not in f[1] and "region" not in f[1]

def test_feature_determinism():
    assert temporal_features([.1,.4,.2]) == temporal_features([.1,.4,.2])

def test_manifest_split_is_deterministic(tmp_path):
    rows=[]
    for i,s in enumerate(["SSB0001","SSB0002","SSB0003","SSB0004","SSB0005"]):
        rows.append({"case_id":f"c{i}","speaker":s,"mechanism":"F5"})
    # This test only checks deterministic speaker assignment; real rows have full feature fields.
    a=prepare_manifest(tmp_path, rows); b=prepare_manifest(tmp_path, rows)
    assert a["speakers"] == b["speakers"]
