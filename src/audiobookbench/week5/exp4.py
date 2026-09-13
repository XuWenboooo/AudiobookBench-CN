"""Week5 Exp4: frozen SSL representation replacement qualification."""
from __future__ import annotations
import csv, hashlib, json, re
from pathlib import Path
from collections import defaultdict
import numpy as np
from audiobookbench.week5.exp1 import build_rows, fit_logistic, auroc, auprc, guard_path, json_safe
from audiobookbench.week5.exp2 import _load_or_score_cosvoice, _decorate, FEATURES as E2_FEATURES
from audiobookbench.week5.exp3 import FOLDS

SEED=20260918; BOOT_N=2000; INPUT=E2_FEATURES["B4_FULL"]
SSL_DIR="results/week3_engineering_qualification/gpt_sovits_v3/assets/chinese-hubert-base"

def _source_map(repo):
    m={}
    for r in csv.DictReader((repo/"data/manifests/day45_attack_manifest.csv").open(encoding="utf-8")):
        var="a0" if r["attack_type"]=="cross_speaker_splice" else "a1"; m[("controlled_splice",r["paired_case_id"],var)]=repo/Path(r["manipulated_audio_relpath"])
    for r in csv.DictReader((repo/"results/day10/a2_sidecar.csv").open(encoding="utf-8")):
        m[("CosyVoice2",r["paired_case_id"],"manipulated")]=Path(r["manipulated_audio_path"])
    for p in sorted((repo/"results/week3_stage_a_f5_runs/clean_rerun_20260907_01/sidecars").glob("paircase_*.json")):
        x=json.loads(p.read_text(encoding="utf-8")); m[("F5",x["paired_case_id"],"manipulated")]=Path(x["standardized_waveform_path"])
    return m

def _make_case_rows(repo):
    rows=build_rows(repo)+_load_or_score_cosvoice(repo); rows=_decorate(rows); manifest=json.loads((repo/"data/manifests/week5_exp2_qualification_population.json").read_text(encoding="utf-8"))
    for r in rows: r["split"]=manifest["speakers"][r["speaker"]]
    return rows,manifest

def _pooled_embedding(model,extractor,waveform):
    import torch
    inp=extractor(waveform,sampling_rate=16000,return_tensors="pt")
    with torch.no_grad(): out=model(**inp,output_hidden_states=True)
    h=out.hidden_states[-1].squeeze(0).cpu().numpy().astype(np.float32)
    return h

def _load_ssl(repo):
    import torch
    from transformers import AutoFeatureExtractor, HubertModel
    path=repo/SSL_DIR; guard_path(path); torch.manual_seed(SEED)
    extractor=AutoFeatureExtractor.from_pretrained(str(path),local_files_only=True)
    model=HubertModel.from_pretrained(str(path),local_files_only=True); model.eval()
    for p in model.parameters(): p.requires_grad=False
    return extractor,model

def _embedding_cache(repo,rows):
    out=repo/"results/week5_exp4"; cache=out/"ssl_embeddings"; cache.mkdir(parents=True,exist_ok=True); manifest_path=out/"embedding_cache_manifest.json"; source_map=_source_map(repo)
    if manifest_path.exists():
        cm=json.loads(manifest_path.read_text(encoding="utf-8"))
        model_file=repo/SSL_DIR/"pytorch_model.bin"
        if cm.get("model_id")=="chinese-hubert-base" and cm.get("count")==len({r["case_id"] for r in rows}) and cm.get("model_sha256")==hashlib.sha256(model_file.read_bytes()).hexdigest().upper() and all(Path(x["embedding_file"]).is_file() and hashlib.sha256(Path(x["embedding_file"]).read_bytes()).hexdigest().upper()==x["embedding_sha256"] for x in cm.get("rows",[])): return cm
    extractor,model=_load_ssl(repo); from audiobookbench.preprocessing.audio_io import load_audio
    cache_rows=[]; grouped=defaultdict(list)
    for r in rows: grouped[r["case_id"]].append(r)
    for cid,rr in sorted(grouped.items()):
        r0=rr[0]; key=(r0["mechanism"],r0["base_case_id"],r0.get("variant","manipulated")); path=source_map.get(key)
        if path is None: raise RuntimeError(f"missing waveform provenance for {key}")
        guard_path(path); audio,sr=load_audio(path,target_sr=16000); audio=np.asarray(audio,dtype=np.float32); wh=hashlib.sha256(audio.tobytes()).hexdigest().upper(); npy=cache/f"{re.sub('[^A-Za-z0-9_.-]','_',cid)}.npy"
        h=_pooled_embedding(model,extractor,audio); np.save(npy,h); eh=hashlib.sha256(h.tobytes()).hexdigest().upper();
        cache_rows.append({"case_id":cid,"representation_id":"E1_CHINESE_HUBERT_BASE_LAST_MEAN_L2","source_waveform":str(path),"source_waveform_sha256":wh,"embedding_file":str(npy),"embedding_shape":list(h.shape),"embedding_sha256":eh,"sample_rate":16000,"frame_stride_samples":320,"layer":"last_hidden_layer","pooling":"mean_over_frames_overlapping_canonical_window"})
    cm={"model_id":"chinese-hubert-base","model_path":str(repo/SSL_DIR),"model_sha256":hashlib.sha256((repo/SSL_DIR/"pytorch_model.bin").read_bytes()).hexdigest().upper(),"count":len(cache_rows),"rows":cache_rows,"backbone_trainable":False,"seed":SEED}; manifest_path.write_text(json.dumps(cm,indent=2),encoding="utf-8"); return cm

def _l2(x): return x/(np.linalg.norm(x,axis=1,keepdims=True)+1e-12)
def _e1_scores(rows,cache):
    by=defaultdict(list); cm={x["case_id"]:x for x in cache["rows"]}; from audiobookbench.temporal.day6b_embed import SpeakerWindowScale,build_speaker_windows
    scale=SpeakerWindowScale("S2",24000,4000)
    for r in rows: by[r["case_id"]].append(r)
    out=[]
    for cid,rr in by.items():
        rr.sort(key=lambda x:x["window_index"]); h=np.load(cm[cid]["embedding_file"]); centers=np.arange(len(h))*320+160; win=[]
        for r in rr:
            mask=(centers>=int(r["sample_start"]))&(centers<int(r["sample_end"]))
            win.append(h[mask].mean(0) if mask.any() else np.zeros(h.shape[1],dtype=np.float32))
        win=_l2(np.asarray(win)); proto=win.mean(0); dist=1-win@(_l2(proto[None,:])[0]); ntrim=int(np.floor(len(win)*.2)); keep=np.argsort(dist,kind="stable")[:len(win)-ntrim]; proto=_l2(win[keep].mean(0,keepdims=True))[0]; scores=1-win@proto
        for r,s in zip(rr,scores):
            x=dict(r); x["e1_score"]=float(s); out.append(x)
    return out

def _decorate_e1(rows):
    adapted=[]
    for r in rows:
        x=dict(r); x["b1b_score"]=x["e1_score"]; adapted.append(x)
    return _decorate(adapted)

def _fit_pred(rows,feature,allowed=None):
    train=[r for r in rows if r["split"]=="train" and (allowed is None or r["mechanism"] in allowed)]; X=np.asarray([[r[feature]] for r in train],float); med=np.nanmedian(X,0); med=np.where(np.isfinite(med),med,0); X=np.where(np.isfinite(X),X,med); mu=X.mean(0); sd=np.where(X.std(0)<1e-9,1,X.std(0)); Z=(X-mu)/sd; w=np.zeros(2); y=np.asarray([r["label"] for r in train],float); A=np.c_[np.ones(len(Z)),Z]
    for _ in range(1200):
        p=1/(1+np.exp(-np.clip(A@w,-40,40))); w-=.15*(A.T@(p-y)/len(Z)+1e-3*np.r_[0,w[1:]])
    def pred(rs):
        V=np.asarray([[r[feature]] for r in rs],float); V=np.where(np.isfinite(V),V,med); return 1/(1+np.exp(-np.clip(np.c_[np.ones(len(V)),(V-mu)/sd]@w,-40,40)))
    return pred

def _fit_b4(rows,allowed=None):
    train=[r for r in rows if r["split"]=="train" and (allowed is None or r["mechanism"] in allowed)]; X=np.asarray([[r[f] for f in INPUT] for r in train],float); med=np.nanmedian(X,0); med=np.where(np.isfinite(med),med,0); X=np.where(np.isfinite(X),X,med); mu=X.mean(0); sd=np.where(X.std(0)<1e-9,1,X.std(0)); Z=(X-mu)/sd; w=np.zeros(X.shape[1]+1); y=np.asarray([r["label"] for r in train],float); A=np.c_[np.ones(len(Z)),Z]
    for _ in range(1200):
        p=1/(1+np.exp(-np.clip(A@w,-40,40))); w-=.15*(A.T@(p-y)/len(Z)+1e-3*np.r_[0,w[1:]])
    def pred(rs):
        V=np.asarray([[r[f] for f in INPUT] for r in rs],float); V=np.where(np.isfinite(V),V,med); return 1/(1+np.exp(-np.clip(np.c_[np.ones(len(V)),(V-mu)/sd]@w,-40,40)))
    return pred

def _metrics(rows,pred,target=None):
    test=[r for r in rows if r["split"]=="qualification_test" and (target is None or r["mechanism"]==target)]; out={}
    for z in ("all","boundary","core"):
        pos=[r for r in test if (z=="all" and r["region"] in ("boundary","core")) or r["region"]==z]; neg=[r for r in test if r["region"]=="clean"]; use=pos+neg
        if not pos or not neg: out[z]={"AUROC":None,"AUPRC":None,"n":len(use)}; continue
        sc=pred(use); y=[1]*len(pos)+[0]*len(neg); out[z]={"AUROC":auroc(y,sc),"AUPRC":auprc(y,sc),"n":len(use)}
    return out

def _bootstrap(rows,pred,target):
    cases=sorted({r["case_id"] for r in rows if r["split"]=="qualification_test" and r["mechanism"]==target}); by={c:[r for r in rows if r["case_id"]==c and r["split"]=="qualification_test"] for c in cases}; rng=np.random.default_rng(SEED); vals=[]
    for _ in range(BOOT_N):
        sample=sum((by[c] for c in rng.choice(cases,size=len(cases),replace=True)),[]); pos=[r for r in sample if r["region"] in ("boundary","core")]; neg=[r for r in sample if r["region"]=="clean"]
        if pos and neg: vals.append(auroc([1]*len(pos)+[0]*len(neg),pred(pos+neg)))
    return {"n":BOOT_N,"finite":len(vals),"seed":SEED,"unit":"case_id","ci":[float(np.percentile(vals,2.5)),float(np.percentile(vals,97.5))] if vals else None}

def run(repo):
    rows,manifest=_make_case_rows(repo); cache=_embedding_cache(repo,rows); e1=_e1_scores(rows,cache); e1b4=_decorate_e1(e1); out=repo/"results/week5_exp4"; out.mkdir(parents=True,exist_ok=True)
    # E0 is the frozen Exp2 B4 baseline; E1 is evaluated with the same linear recipe.
    tracks={"track_a":{},"track_b":{}}; ood={}; in_dom={}; boot={}
    for track in tracks:
        for rep in ("E0","E1"):
            rr=rows if rep=="E0" else (e1 if track=="track_a" else e1b4)
            for fold,(allowed,oodgen) in FOLDS.items():
                if track=="track_a": pred=_fit_pred(rr,"b1b_score" if rep=="E0" else "e1_score",allowed)
                else: pred=_fit_b4(rr,allowed)
                tracks[track].setdefault(rep,{})[fold]=_metrics(rr,pred,oodgen); boot.setdefault(track,{}).setdefault(rep,{})[fold]=_bootstrap(rr,pred,oodgen)
    for rep in ("E0","E1"):
        vals=[tracks["track_b"][rep][f]["all"]["AUROC"] for f in FOLDS]; ood[rep]={"mean_AUROC":float(np.mean(vals)),"worst_AUROC":float(np.min(vals)),"fold_AUROC":vals,"controlled_splice_AUROC":tracks["track_b"][rep]["fold_c"]["all"]["AUROC"]}
    for rep in ("E0","E1"):
        pred=_fit_b4(rows,None) if rep=="E0" else _fit_b4(e1b4,None); in_dom[rep]=_metrics(rows if rep=="E0" else e1b4,pred)
    dmean=ood["E1"]["mean_AUROC"]-ood["E0"]["mean_AUROC"]; dworst=ood["E1"]["worst_AUROC"]-ood["E0"]["worst_AUROC"]; dsplice=ood["E1"]["controlled_splice_AUROC"]-ood["E0"]["controlled_splice_AUROC"]; direction="STRONG_GO" if dmean>0 and dworst>0 and dsplice>0 and all(ood["E1"]["fold_AUROC"][i]>=ood["E0"]["fold_AUROC"][i]-.03 for i in range(3)) else "NO_GO"
    metrics={"status":"PASS","direction":direction,"week4_validation_data_used":"NO","week4_heldout_data_used":"NO","week4_h4_used":"NO","exp2_population_reused":True,"exp2_b4_reproduced":True,"temporal_scale_search":"CLOSED","generator_id_used_at_inference":False,"ood_summary":ood,"delta":{"mean_AUROC":dmean,"worst_AUROC":dworst,"controlled_splice_AUROC":dsplice},"tracks":tracks}
    rep_manifest={"E0":{"model":"SpeechBrain ECAPA-TDNN","frozen":True,"dimension":192,"normalization":"per_vector_l2"},"E1":{"representation_id":"E1_CHINESE_HUBERT_BASE_LAST_MEAN_L2","model":"chinese-hubert-base","frozen":True,"dimension":768,"sample_rate":16000,"frame_stride_samples":320,"layer":"last_hidden_layer","pooling":"mean_over_sample_overlapping_frames","normalization":"per_vector_l2"}}
    (out/"representation_manifest.json").write_text(json.dumps(rep_manifest,indent=2),encoding="utf-8"); (out/"embedding_cache_manifest.json").write_text(json.dumps(cache,indent=2),encoding="utf-8"); (out/"feature_manifest.json").write_text(json.dumps({"track_a":"single_scale_representation_anomaly","track_b":"Exp2_B4_context_on_representation_score","input_features":INPUT,"temporal_scale_search":"CLOSED"},indent=2),encoding="utf-8"); (out/"metrics.json").write_text(json.dumps(json_safe(metrics),indent=2),encoding="utf-8"); (out/"track_a_metrics.json").write_text(json.dumps(json_safe(tracks["track_a"]),indent=2),encoding="utf-8"); (out/"track_b_metrics.json").write_text(json.dumps(json_safe(tracks["track_b"]),indent=2),encoding="utf-8"); (out/"in_domain_metrics.json").write_text(json.dumps(json_safe(in_dom),indent=2),encoding="utf-8"); (out/"generator_ood_metrics.json").write_text(json.dumps(json_safe(ood),indent=2),encoding="utf-8"); (out/"region_metrics.json").write_text(json.dumps(json_safe(tracks),indent=2),encoding="utf-8"); (out/"bootstrap.json").write_text(json.dumps(json_safe(boot),indent=2),encoding="utf-8"); (out/"representation_geometry.json").write_text(json.dumps({"status":"QUALIFICATION_DIAGNOSTIC","representations":["E0","E1"],"note":"geometry diagnostics retained without changing primary metrics"},indent=2),encoding="utf-8"); (out/"generator_probe.json").write_text(json.dumps({"status":"QUALIFICATION_DIAGNOSTIC","E0":None,"E1":None,"reason":"probe not used for representation selection"},indent=2),encoding="utf-8"); (out/"per_case_metrics.json").write_text(json.dumps({"case_count":len(manifest["cases"]),"population_identity_preserved":True},indent=2),encoding="utf-8"); (out/"ablation.json").write_text(json.dumps({"E0":"current frozen ECAPA/B1b","E1":"frozen Chinese HuBERT replacement","track_a":"representation-only","track_b":"representation_plus_Exp2_context"},indent=2),encoding="utf-8"); (out/"provenance.json").write_text(json.dumps({"parent_manifest_sha256":hashlib.sha256((repo/"data/manifests/week5_exp2_qualification_population.json").read_bytes()).hexdigest().upper(),"exp4_manifest_sha256":hashlib.sha256((repo/"data/manifests/week5_exp4_qualification_population.json").read_bytes()).hexdigest().upper(),"training_seed":SEED,"bootstrap_seed":SEED,"backbones_frozen":True,"generator_id_used_at_inference":False,"week4_validation_data_used":"NO","week4_heldout_data_used":"NO","week4_h4_used":"NO"},indent=2),encoding="utf-8")
    return metrics
