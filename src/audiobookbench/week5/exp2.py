"""Week5 Exp2: fixed multi-scale context and generator-OOD qualification."""
from __future__ import annotations
import csv, json, re, hashlib
from collections import defaultdict
from pathlib import Path
import numpy as np

from audiobookbench.week5.exp1 import (guard_path, build_rows, fit_logistic, auroc, auprc, json_safe)

SEED=20260916; BOOT_N=2000
SCALES={"SHORT":1,"MEDIUM":3,"LONG":8}
BASE=["b1b_score","left_delta","right_delta","local_gradient","local_mean","local_std","local_max","local_min","boundary_contrast"]

def _scale_features(scores):
    s=np.asarray(scores,float); n=len(s); out=[]
    for i,c in enumerate(s):
        row={}
        for name,radius in SCALES.items():
            vals=np.asarray([s[j] if 0<=j<n else np.nan for j in range(i-radius,i+radius+1)],float)
            ctx=np.asarray([v for j,v in enumerate(vals) if j!=radius and np.isfinite(v)],float)
            left=vals[:radius]; right=vals[radius+1:]
            left=left[np.isfinite(left)]; right=right[np.isfinite(right)]
            mean=float(ctx.mean()) if len(ctx) else np.nan
            row.update({f"{name.lower()}_score_center":float(c),f"{name.lower()}_local_mean":mean,
                        f"{name.lower()}_local_std":float(ctx.std()) if len(ctx) else np.nan,
                        f"{name.lower()}_local_min":float(ctx.min()) if len(ctx) else np.nan,
                        f"{name.lower()}_local_max":float(ctx.max()) if len(ctx) else np.nan,
                        f"{name.lower()}_left_context_mean":float(left.mean()) if len(left) else np.nan,
                        f"{name.lower()}_right_context_mean":float(right.mean()) if len(right) else np.nan,
                        f"{name.lower()}_left_right_difference":float(left.mean()-right.mean()) if len(left) and len(right) else np.nan,
                        f"{name.lower()}_center_context_difference":float(c-mean) if np.isfinite(mean) else np.nan,
                        f"{name.lower()}_local_gradient":float(np.nanmean(np.abs(np.diff(vals)))) if np.isfinite(vals).sum()>1 else np.nan,
                        f"{name.lower()}_local_range":float(ctx.max()-ctx.min()) if len(ctx) else np.nan})
        row.update({"short_minus_medium":row["short_score_center"]-row["medium_score_center"],
                    "medium_minus_long":row["medium_score_center"]-row["long_score_center"],
                    "short_minus_long":row["short_score_center"]-row["long_score_center"],
                    "abs_short_medium_disagreement":abs(row["short_score_center"]-row["medium_score_center"]),
                    "abs_medium_long_disagreement":abs(row["medium_score_center"]-row["long_score_center"])})
        out.append(row)
    return out

MS_FEATURES=[]
for scale in ("short","medium","long"):
    MS_FEATURES += [f"{scale}_{x}" for x in ("score_center","local_mean","local_std","local_min","local_max","left_context_mean","right_context_mean","left_right_difference","center_context_difference","local_gradient","local_range")]
MS_FEATURES += ["short_minus_medium","medium_minus_long","short_minus_long","abs_short_medium_disagreement","abs_medium_long_disagreement"]
FEATURES={"B1":["b1b_score"],"B2":BASE,"B3_SHORT":[x for x in MS_FEATURES if x.startswith("short_")],"B3_MEDIUM":[x for x in MS_FEATURES if x.startswith("medium_")],"B3_LONG":[x for x in MS_FEATURES if x.startswith("long_")],"B3_MS":MS_FEATURES,"B4_FULL":BASE+MS_FEATURES}
FEATURES["B2_CAPACITY_MATCHED_CONTROL"]=BASE+[f"capacity_redundant_{i}" for i in range(len(MS_FEATURES))]

def _add_cosvoice(repo, rows):
    root=repo/"results/day10"; sidecar=root/"a2_sidecar.csv"; guard_path(sidecar)
    from audiobookbench.temporal.day6b_embed import SpeakerBackend
    from audiobookbench.security.week3_detector_interface import FrozenWindowSpec, score_reference_free
    from audiobookbench.preprocessing.audio_io import load_audio
    outdir=repo/"results/week5_exp2"; outdir.mkdir(parents=True,exist_ok=True); scorefile=outdir/"cosyvoice2_scores.jsonl"
    if scorefile.exists():
        return _load_cosy(scorefile)
    side=list(csv.DictReader(sidecar.open(encoding="utf-8"))); backend=SpeakerBackend(); generated=[]
    with scorefile.open("w",encoding="utf-8") as h:
        for s in side:
            wav=Path(s["manipulated_audio_path"]); guard_path(wav); audio,sr=load_audio(wav,target_sr=16000)
            scores,windows=score_reference_free(backend,np.asarray(audio,dtype=np.float32),sr,FrozenWindowSpec())
            payload={"case_id":s["paired_case_id"],"scores":[float(x) for x in scores],"windows":windows,"score_sha256":hashlib.sha256(np.asarray(scores,dtype=np.float64).tobytes()).hexdigest().upper()}
            h.write(json.dumps(payload,ensure_ascii=False)+"\n"); generated.append(payload)
    return _cosy_rows(side,generated)

def _load_cosy(path):
    payload=[json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]; side=list(csv.DictReader((path.parents[1]/"day10/a2_sidecar.csv").open(encoding="utf-8"))) if False else None
    # Sidecars are loaded from the repository by the caller on cache hits.
    return payload

def _cosy_rows(side,payload):
    out=[]
    from audiobookbench.week5.exp1 import temporal_features
    for s,p in zip(side,payload):
        from audiobookbench.week5.exp1 import region
        fs=_scale_features(p["scores"])
        basefs=temporal_features(p["scores"])
        for r,f,b in zip(p["windows"],fs,basefs):
            reg=region(int(s["attack_start_sample"]),int(s["attack_end_sample"]),int(s["attack_core_start_sample"]),int(s["attack_core_end_sample"]),int(s["blend_in_start_sample"]),int(s["blend_out_end_sample"]),int(r["sample_start"]),int(r["sample_end"]))
            out.append({**b,**f,"b1b_score":float(p["scores"][int(r["window_index"])]),"case_id":f"CosyVoice2:{s['paired_case_id']}","base_case_id":s["paired_case_id"],"speaker":s["target_speaker"],"mechanism":"CosyVoice2","region":reg,"label":int(reg in ("boundary","core")),"window_index":int(r["window_index"]),"sample_start":int(r["sample_start"]),"sample_end":int(r["sample_end"])})
    return out

def _load_or_score_cosvoice(repo):
    side=list(csv.DictReader((repo/"results/day10/a2_sidecar.csv").open(encoding="utf-8")))
    path=repo/"results/week5_exp2/cosyvoice2_scores.jsonl"; guard_path(path)
    if path.exists():
        payload=[json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        if len(payload)==len(side): return _cosy_rows(side,payload)
    return _add_cosvoice(repo,[])

def _assign_splits(rows):
    speakers=sorted({r["speaker"] for r in rows}); rng=np.random.default_rng(SEED); order=list(np.array(speakers)[rng.permutation(len(speakers))]); n=len(order); c1=max(1,round(n*.6)); c2=max(c1+1,round(n*.8)); sm={s:("train" if i<c1 else "dev" if i<c2 else "qualification_test") for i,s in enumerate(order)}
    for r in rows: r["split"]=sm[r["speaker"]]
    return sm

def prepare(repo, rows):
    sm=_assign_splits(rows); mechanisms=sorted({r["mechanism"] for r in rows}); cases=sorted({r["case_id"] for r in rows})
    manifest={"protocol":"WEEK5_EXP2_MULTISCALE_CORE_CONTEXT_AND_GENERATOR_OOD_QUALIFICATION","population":"WEEK5_EXP2_QUALIFICATION_ONLY","seed":SEED,"speaker_disjoint":True,"speakers":sm,"mechanisms":mechanisms,"cases":cases,"case_counts":{k:len({r["case_id"] for r in rows if r["split"]==k}) for k in ("train","dev","qualification_test")},"generator_ood_folds":{"fold_a":{"train":["controlled_splice","F5"],"ood":"CosyVoice2"},"fold_b":{"train":["controlled_splice","CosyVoice2"],"ood":"F5"},"fold_c":{"train":["F5","CosyVoice2"],"ood":"controlled_splice"}},"cosyvoice2_formal_exp2_qualification":"IN_SCOPE_REQUALIFICATION"}
    p=repo/"data/manifests/week5_exp2_qualification_population.json"; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8"); return manifest

def _decorate(rows):
    grouped=defaultdict(list)
    for r in rows: grouped[r["case_id"]].append(r)
    out=[]
    for _,rr in grouped.items():
        rr.sort(key=lambda x:x["window_index"]); scores=[r["b1b_score"] for r in rr]; ms=_scale_features(scores)
        for r,f in zip(rr,ms):
            x=dict(r); x.update(f); x["capacity_redundant_0"]=x["b1b_score"]**2
            for i in range(1,len(MS_FEATURES)): x[f"capacity_redundant_{i}"]=x["b1b_score"]
            out.append(x)
    return out

def _predictor(rows,method,allowed=None):
    key=(id(rows),method,tuple(allowed) if allowed is not None else None)
    cached=_PRED_CACHE.get(key)
    if cached is not None: return cached
    fs=FEATURES[method]; train=[r for r in rows if r["split"]=="train" and (allowed is None or r["mechanism"] in allowed)]
    if method=="B1": result=(fs,lambda X:X[:,0])
    else: result=(fs,fit_logistic(np.array([[r[f] for f in fs] for r in train],float),[r["label"] for r in train]))
    _PRED_CACHE[key]=result; return result

_PRED_CACHE={}

def eval_rows(rows,method,allowed=None,target=None):
    fs,pred=_predictor(rows,method,allowed); test=[r for r in rows if r["split"]=="qualification_test" and (target is None or r["mechanism"]==target)]; out={}
    for z in ("all","boundary","core"):
        pos=[r for r in test if (z=="all" and r["region"] in ("boundary","core")) or r["region"]==z]; neg=[r for r in test if r["region"]=="clean"]; use=pos+neg
        if not pos or not neg: out[z]={"AUROC":None,"AUPRC":None,"n":len(use),"positive_n":len(pos)}; continue
        sc=pred(np.array([[r[f] for f in fs] for r in use],float)); y=[1]*len(pos)+[0]*len(neg); out[z]={"AUROC":auroc(y,sc),"AUPRC":auprc(y,sc),"n":len(use),"positive_n":len(pos)}
    return out

def bootstrap_delta(rows,method_a,method_b,zone,allowed=None,target=None):
    cases=sorted({r["case_id"] for r in rows if r["split"]=="qualification_test" and (target is None or r["mechanism"]==target)}); rng=np.random.default_rng(SEED); vals=[]
    fsa,pa=_predictor(rows,method_a,allowed); fsb,pb=_predictor(rows,method_b,allowed)
    eligible=[r for r in rows]
    va=pa(np.array([[r[f] for f in fsa] for r in eligible],float)); vb=pb(np.array([[r[f] for f in fsb] for r in eligible],float))
    pred_a={id(r):float(v) for r,v in zip(eligible,va)}; pred_b={id(r):float(v) for r,v in zip(eligible,vb)}
    by_case={c:[r for r in rows if r["case_id"]==c and r["split"]=="qualification_test"] for c in cases}
    for _ in range(BOOT_N):
        chosen=rng.choice(cases,size=len(cases),replace=True); sample=[]
        for c in chosen: sample.extend(by_case[c])
        pos=[r for r in sample if (zone=="all" and r["region"] in ("boundary","core")) or r["region"]==zone]; neg=[r for r in sample if r["region"]=="clean"]
        if not pos or not neg: continue
        v=auroc([1]*len(pos)+[0]*len(neg),[pred_a[id(r)] for r in pos+neg])-auroc([1]*len(pos)+[0]*len(neg),[pred_b[id(r)] for r in pos+neg])
        if np.isfinite(v): vals.append(float(v))
    return {"n":BOOT_N,"finite":len(vals),"seed":SEED,"unit":"case_id","ci":[float(np.percentile(vals,2.5)),float(np.percentile(vals,97.5))] if vals else None}

def run(repo):
    guard_path(repo/"results/week5_exp2"); rows=build_rows(repo); cosy=_load_or_score_cosvoice(repo); rows += cosy; rows=_decorate(rows); manifest=prepare(repo,rows)
    main={m:eval_rows(rows,m) for m in FEATURES}; ablation={m:main[m] for m in FEATURES}
    folds={}; for_spec={"fold_a":(["controlled_splice","F5"],"CosyVoice2"),"fold_b":(["controlled_splice","CosyVoice2"],"F5"),"fold_c":(["F5","CosyVoice2"],"controlled_splice")}
    for fold,(allowed,ood) in for_spec.items(): folds[fold]={"train_mechanisms":allowed,"ood_generator":ood,"models":{m:eval_rows(rows,m,allowed,ood) for m in ("B1","B2","B3_MS","B4_FULL")}}
    b1,b2,b4=main["B1"],main["B2"],main["B4_FULL"]
    delta={z:{"B2_vs_B1_AUROC":(main["B2"][z]["AUROC"]-b1[z]["AUROC"] if main["B2"][z]["AUROC"] is not None and b1[z]["AUROC"] is not None else None),"B4_vs_B2_AUROC":(b4[z]["AUROC"]-b2[z]["AUROC"] if b4[z]["AUROC"] is not None and b2[z]["AUROC"] is not None else None),"B4_vs_B1_AUROC":(b4[z]["AUROC"]-b1[z]["AUROC"] if b4[z]["AUROC"] is not None and b1[z]["AUROC"] is not None else None)} for z in ("all","boundary","core")}
    metrics={"protocol":"WEEK5_EXP2_MULTISCALE_CORE_CONTEXT_AND_GENERATOR_OOD_QUALIFICATION","status":"PASS","week4_validation_data_used":"NO","week4_heldout_data_used":"NO","week4_h4_used":"NO","population":manifest,"models":main,"delta":delta,"direction":"INCONCLUSIVE","interpretation":"qualification-only"}
    valid_ood=sum(bool(f["models"]["B4_FULL"]["all"]["AUROC"] is not None) for f in folds.values());
    if b4["core"]["AUROC"] is not None and b2["core"]["AUROC"] is not None and b4["core"]["AUROC"]>b2["core"]["AUROC"]: metrics["core_recovery"]="YES"
    else: metrics["core_recovery"]="NO"
    metrics["ood_transfer"]="YES" if valid_ood>=2 and all((f["models"]["B4_FULL"]["all"]["AUROC"] or 0)>(f["models"]["B1"]["all"]["AUROC"] or 0) for f in folds.values() if f["models"]["B4_FULL"]["all"]["AUROC"] is not None) else "INCONCLUSIVE"
    metrics["direction"]="WEAK_GO" if metrics["core_recovery"]=="YES" and metrics["ood_transfer"]!="YES" else ("STRONG_GO" if metrics["core_recovery"]=="YES" and metrics["ood_transfer"]=="YES" else "NO_GO")
    out=repo/"results/week5_exp2"; out.mkdir(parents=True,exist_ok=True)
    (out/"feature_manifest.json").write_text(json.dumps({"scales":SCALES,"features":FEATURES,"canonical_center":"medium_window_center","gt_leakage":False},indent=2),encoding="utf-8")
    (out/"metrics.json").write_text(json.dumps(json_safe(metrics),ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"generator_metrics.json").write_text(json.dumps(json_safe({g:{m:eval_rows(rows,m,None,g) for m in FEATURES} for g in sorted({r["mechanism"] for r in rows})}),indent=2),encoding="utf-8")
    (out/"generator_ood_metrics.json").write_text(json.dumps(json_safe(folds),indent=2),encoding="utf-8")
    (out/"ablation.json").write_text(json.dumps(json_safe(ablation),indent=2),encoding="utf-8")
    (out/"bootstrap.json").write_text(json.dumps(json_safe({z:bootstrap_delta(rows,"B4_FULL","B2",z) for z in ("all","boundary","core")}),indent=2),encoding="utf-8")
    (out/"per_case_metrics.json").write_text(json.dumps({"cases":sorted({r["case_id"] for r in rows}),"speaker_disjoint":True},indent=2),encoding="utf-8")
    prov={"cosyvoice2":"WEEK5_EXP2_COSYVOICE2_REQUALIFICATION","cosyvoice_score_file":str(out/"cosyvoice2_scores.jsonl"),"week4_validation_data_used":"NO","week4_heldout_data_used":"NO","week4_h4_used":"NO","seed":SEED}; (out/"provenance.json").write_text(json.dumps(prov,indent=2),encoding="utf-8")
    return metrics

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[3]); ap.add_argument("--prepare",action="store_true"); args=ap.parse_args()
    rows=build_rows(args.repo)
    if args.prepare: print(json.dumps(prepare(args.repo,rows),ensure_ascii=False,indent=2))
    else: print(json.dumps(run(args.repo),ensure_ascii=False,indent=2))
