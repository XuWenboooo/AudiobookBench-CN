"""Week5 Exp1 qualification: frozen B1b versus a small boundary-aware model."""
from __future__ import annotations

import csv, hashlib, json, math, re
from pathlib import Path
from collections import defaultdict
import numpy as np

FORBIDDEN = ("week4_validation", "held_out", "week4_adaptive_redteam_runs")

def guard_path(path: str | Path) -> None:
    s = str(path).replace("\\", "/").lower()
    if any(t in s for t in FORBIDDEN) or re.search(r"held", s):
        raise RuntimeError(f"Week4/held-out path rejected: {path}")

def auroc(y, score):
    y, score = np.asarray(y, int), np.asarray(score, float)
    m = np.isfinite(score); y, score = y[m], score[m]
    if len(np.unique(y)) < 2: return float("nan")
    order = np.argsort(score, kind="stable"); yy = y[order]
    pos, neg = yy.sum(), len(yy)-yy.sum()
    ranks = np.arange(1, len(yy)+1, dtype=float)
    return float((ranks[yy == 1].sum() - pos*(pos+1)/2) / (pos*neg))

def auprc(y, score):
    y, score = np.asarray(y, int), np.asarray(score, float)
    m = np.isfinite(score); y, score = y[m], score[m]
    if len(np.unique(y)) < 2: return float("nan")
    order = np.argsort(-score, kind="stable"); y = y[order]
    tp = np.cumsum(y); fp = np.cumsum(1-y); total = tp[-1]
    if total == 0: return float("nan")
    return float(np.sum((tp / np.maximum(tp+fp, 1)) * y) / total)

def overlap(a, b, lo, hi):
    return max(0, min(b, hi)-max(a, lo)) / max(1, b-a)

def region(start, end, core_start, core_end, blend_start, blend_end, ws, we):
    attack = overlap(ws, we, start, end); core = overlap(ws, we, core_start, core_end)
    blend = overlap(ws, we, blend_start, blend_end)
    if attack == 0: return "clean"
    if core >= .5 and blend == 0: return "core"
    return "boundary"

def temporal_features(scores):
    s = np.asarray(scores, float); n=len(s); out=[]
    for i, c in enumerate(s):
        left = s[i-1] if i else np.nan; right = s[i+1] if i+1<n else np.nan
        nb = np.asarray([left, right], float); nb=nb[np.isfinite(nb)]
        mean=float(nb.mean()) if len(nb) else np.nan
        out.append({"b1b_score":float(c), "left_delta":float(c-left) if np.isfinite(left) else np.nan,
                    "right_delta":float(c-right) if np.isfinite(right) else np.nan,
                    "local_gradient":float(abs(c-left)+abs(c-right))/2 if np.isfinite(left) and np.isfinite(right) else np.nan,
                    "local_mean":mean, "local_std":float(nb.std()) if len(nb) else np.nan,
                    "local_max":float(nb.max()) if len(nb) else np.nan, "local_min":float(nb.min()) if len(nb) else np.nan,
                    "boundary_contrast":float(c-mean) if np.isfinite(mean) else np.nan})
    return out

def _read_controlled(repo):
    path=repo/"results/day6b/speaker_scores.csv"; guard_path(path)
    rows=list(csv.DictReader(path.open(encoding="utf-8")))
    rows=[r for r in rows if r["scale"]=="S2_1500ms_250ms"]
    by=defaultdict(list)
    for r in rows: by[(r["paired_case_id"],r["variant"])].append(r)
    out=[]
    for (cid,var), rr in sorted(by.items()):
        rr.sort(key=lambda x:int(x["window_index"])); scores=[float(x["B1b"]) for x in rr]
        sp=re.search(r"SSB\d+", rr[0]["record_id"]); speaker=sp.group(0) if sp else "UNKNOWN"
        fs=temporal_features(scores)
        for r,f in zip(rr,fs):
            out.append({**f,"case_id":f"controlled_splice:{cid}:{var}","base_case_id":cid,"variant":var,"speaker":speaker,
                        "mechanism":"controlled_splice","split_source":r["split"],"window_index":int(r["window_index"]),
                        "region":("clean" if r["zone"].lower()=="outside" else r["zone"].lower()),"label":int(float(r["attack_overlap_ratio"])>=.5),
                        "sample_start":int(r["sample_start"]),"sample_end":int(r["sample_end"])})
    return out

def _read_f5(repo):
    root=repo/"results/week3_stage_a_f5_runs/clean_rerun_20260907_01"; guard_path(root)
    timeline=repo/"results/week3_evaluation_repro_runs/week3_eval_repro_20260907_01/evidence/window_timeline.jsonl"; guard_path(timeline)
    side={}
    for p in sorted((root/"sidecars").glob("paircase_*.json")):
        guard_path(p); x=json.loads(p.read_text(encoding="utf-8")); side[x["paired_case_id"]]=x
    grouped=defaultdict(list)
    for line in timeline.read_text(encoding="utf-8").splitlines():
        if line.strip():
            x=json.loads(line); grouped[x["paired_case_id"]].append(x)
    out=[]
    for cid, rr in sorted(grouped.items()):
        if cid not in side: continue
        s=side[cid]; rr.sort(key=lambda x:int(x["window_index"])); scores=[float(x["score"]) for x in rr]; fs=temporal_features(scores)
        for r,f in zip(rr,fs):
            reg=region(int(s["attack_start_sample"]),int(s["attack_end_sample"]),int(s["attack_core_start_sample"]),int(s["attack_core_end_sample"]),int(s["blend_in_start_sample"]),int(s["blend_out_end_sample"]),int(r["sample_start"]),int(r["sample_end"]))
            out.append({**f,"case_id":f"F5:{cid}","base_case_id":cid,"variant":"manipulated","speaker":s["target_speaker"],"mechanism":"F5",
                        "split_source":s["split"],"window_index":int(r["window_index"]),"region":reg,"label":int(reg in ("boundary","core")),
                        "sample_start":int(r["sample_start"]),"sample_end":int(r["sample_end"])})
    return out

def build_rows(repo): return _read_controlled(repo)+_read_f5(repo)

def prepare_manifest(repo, rows):
    speakers=sorted({r["speaker"] for r in rows}); rng=np.random.default_rng(20260915); speakers=list(np.array(speakers)[rng.permutation(len(speakers))])
    n=len(speakers); cuts=(max(1,round(n*.6)), max(2,round(n*.8))); sm={s:("train" if i<cuts[0] else "dev" if i<cuts[1] else "qualification_test") for i,s in enumerate(speakers)}
    for r in rows: r["split"]=sm[r["speaker"]]
    manifest={"protocol":"WEEK5_EXP1_BOUNDARY_CORE_RECOVERABILITY_QUALIFICATION","population":"WEEK5_EXP1_QUALIFICATION_ONLY","seed":20260915,
              "week4_used":"NO","speaker_disjoint":True,"speakers":sm,"cases":sorted({r["case_id"] for r in rows}),
              "case_counts":{k:len({r["case_id"] for r in rows if r["split"]==k}) for k in ("train","dev","qualification_test")},
              "mechanisms":sorted({r["mechanism"] for r in rows}),"cosyvoice_score_evidence":"MISSING_NOT_USED"}
    target=repo/"data/manifests/week5_exp1_qualification_population.json"; target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    return manifest

def fit_logistic(X,y):
    med=np.nanmedian(X,axis=0); med=np.where(np.isfinite(med),med,0); X=np.where(np.isfinite(X),X,med); mu=X.mean(0); sd=X.std(0); sd=np.where(sd<1e-9,1,sd); Z=(X-mu)/sd
    w=np.zeros(Z.shape[1]+1); yy=np.asarray(y,float)
    for _ in range(1200):
        p=1/(1+np.exp(-np.clip(np.c_[np.ones(len(Z)),Z]@w,-40,40))); g=np.c_[np.ones(len(Z)),Z].T@(p-yy)/len(Z)+1e-3*np.r_[0,w[1:]]; w-=.15*g
    return lambda X: 1/(1+np.exp(-np.clip(np.c_[np.ones(len(X)),(np.where(np.isfinite(X),X,med)-mu)/sd]@w,-40,40)))

FEATURES={"B1":["b1b_score"],"B2a":["b1b_score","left_delta","right_delta","local_gradient","boundary_contrast"],"B2b":["b1b_score","local_mean","local_std","local_max","local_min","boundary_contrast"],"B2-full":["b1b_score","left_delta","right_delta","local_gradient","local_mean","local_std","local_max","local_min","boundary_contrast"]}

def json_safe(x):
    if isinstance(x, dict): return {k:json_safe(v) for k,v in x.items()}
    if isinstance(x, list): return [json_safe(v) for v in x]
    if isinstance(x, float) and not math.isfinite(x): return None
    return x

def evaluate(rows, method, subset=None):
    fs=FEATURES[method]; rr=[r for r in rows if subset is None or r["mechanism"]==subset]; out={}
    train=[r for r in rows if r["split"]=="train"]; test=[r for r in rr if r["split"]=="qualification_test"]
    if method=="B1": pred=lambda X:X[:,0]
    else: pred=fit_logistic(np.array([[r[f] for f in fs] for r in train],float),[r["label"] for r in train])
    for zone in ("all","boundary","core"):
        pos=[r for r in test if (zone=="all" and r["region"] in ("boundary","core")) or r["region"]==zone]
        neg=[r for r in test if r["region"]=="clean"]; use=pos+neg
        if not use: out[zone]={"AUROC":None,"AUPRC":None,"n":0}; continue
        X=np.array([[r[f] for f in fs] for r in use],float); sc=pred(X); y=[r["label"] if r in pos else 0 for r in use]
        out[zone]={"AUROC":auroc(y,sc),"AUPRC":auprc(y,sc),"n":len(use),"positive_n":sum(y)}
    return out

def bootstrap_delta(rows, zone, n=2000, seed=20260915):
    """Case-level percentile CI for B2-full minus B1; windows are never resampled."""
    test=[r for r in rows if r["split"]=="qualification_test"]
    cases=sorted({r["case_id"] for r in test}); rng=np.random.default_rng(seed); vals=[]
    train=[r for r in rows if r["split"]=="train"]
    pred2=fit_logistic(np.array([[r[f] for f in FEATURES["B2-full"]] for r in train],float),[r["label"] for r in train])
    case_arrays={}
    for c in cases:
        cr=[r for r in test if r["case_id"]==c]
        def one(m, pred):
            fs=FEATURES[m]; pos=[r for r in cr if (zone=="all" and r["region"] in ("boundary","core")) or r["region"]==zone]; neg=[r for r in cr if r["region"]=="clean"]; use=pos+neg
            return np.asarray([1]*len(pos)+[0]*len(neg)), pred(np.array([[r[f] for f in fs] for r in use],float))
        y1,s1=one("B1",lambda X:X[:,0]); y2,s2=one("B2-full",pred2)
        case_arrays[c]=(y1,s1,y2,s2)
    for _ in range(n):
        sampled=rng.choice(cases,size=len(cases),replace=True)
        y1=np.concatenate([case_arrays[c][0] for c in sampled]); s1=np.concatenate([case_arrays[c][1] for c in sampled])
        y2=np.concatenate([case_arrays[c][2] for c in sampled]); s2=np.concatenate([case_arrays[c][3] for c in sampled])
        v=auroc(y2,s2)-auroc(y1,s1)
        if np.isfinite(v): vals.append(float(v))
    return {"n":n,"finite":len(vals),"seed":seed,"unit":"case_id","ci":[float(np.percentile(vals,2.5)),float(np.percentile(vals,97.5))] if vals else None}

def run(repo):
    # Guard every actual input path at its point of access; do not probe forbidden
    # sentinel paths here because the guard must fail closed on those exact names.
    rows=build_rows(repo); manifest=prepare_manifest(repo,rows)
    # B1 and B2 are computed once with fixed split; no threshold is selected.
    metrics={"protocol":"WEEK5_EXP1_BOUNDARY_CORE_RECOVERABILITY_QUALIFICATION","status":"PASS","week4_validation_data_used":"NO","week4_heldout_data_used":"NO","week4_h4_used":"NO","population":manifest}
    metrics["overall"]={m:evaluate(rows,m) for m in FEATURES}
    metrics["by_generator"]={g:{m:evaluate(rows,m,g) for m in FEATURES} for g in sorted({r["mechanism"] for r in rows})}
    b1=metrics["overall"]["B1"]; b2=metrics["overall"]["B2-full"]; metrics["delta"]={z:{"AUROC":(b2[z]["AUROC"]-b1[z]["AUROC"] if b1[z]["AUROC"] is not None and b2[z]["AUROC"] is not None else None),"AUPRC":(b2[z]["AUPRC"]-b1[z]["AUPRC"] if b1[z]["AUPRC"] is not None and b2[z]["AUPRC"] is not None else None)} for z in ("all","boundary","core")}
    metrics["generator_ood"]="NOT_REPORTABLE_FOR_STRONG_CLAIM"
    metrics["direction"]="INCONCLUSIVE" if "controlled_splice" not in metrics["by_generator"] or "F5" not in metrics["by_generator"] else ("WEAK_GO" if metrics["delta"]["boundary"]["AUROC"]>0 else "NO_GO")
    metrics["bootstrap"]={z:bootstrap_delta(rows,z) for z in ("all","boundary","core")}
    out=repo/"results/week5_exp1"; out.mkdir(parents=True,exist_ok=True)
    (out/"metrics.json").write_text(json.dumps(json_safe(metrics),ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
    per_case={}
    for c in sorted({r["case_id"] for r in rows if r["split"]=="qualification_test"}):
        cr=[r for r in rows if r["case_id"]==c]; per_case[c]={"mechanism":cr[0]["mechanism"],"speaker":cr[0]["speaker"],"B1":evaluate(rows,"B1",cr[0]["mechanism"]),"B2-full":evaluate(rows,"B2-full",cr[0]["mechanism"])}
    (out/"per_case_metrics.json").write_text(json.dumps(json_safe(per_case),ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"feature_manifest.json").write_text(json.dumps({"features":FEATURES,"gt_fields_not_used_as_input":True,"deterministic":True},indent=2),encoding="utf-8")
    (out/"bootstrap.json").write_text(json.dumps(json_safe(metrics["bootstrap"]),indent=2),encoding="utf-8")
    return metrics

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[3]); ap.add_argument("--prepare",action="store_true"); args=ap.parse_args()
    rows=build_rows(args.repo); print(json.dumps(prepare_manifest(args.repo,rows) if args.prepare else run(args.repo),ensure_ascii=False,indent=2))
