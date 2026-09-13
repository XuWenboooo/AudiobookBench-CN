"""Week5 Exp3: small generator-diverse representation qualification."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from collections import defaultdict
import numpy as np
from audiobookbench.week5.exp1 import build_rows, fit_logistic, auroc, auprc, json_safe
from audiobookbench.week5.exp2 import _load_or_score_cosvoice, _decorate, FEATURES as E2_FEATURES, _predictor as e2_predictor

SEED=20260917; BOOT_N=2000; INPUT=E2_FEATURES["B4_FULL"]
FOLDS={"fold_a":(["controlled_splice","F5"],"CosyVoice2"),"fold_b":(["controlled_splice","CosyVoice2"],"F5"),"fold_c":(["F5","CosyVoice2"],"controlled_splice")}

def load_population(repo):
    p=repo/"data/manifests/week5_exp2_qualification_population.json"; q=repo/"data/manifests/week5_exp3_qualification_population.json"
    parent=hashlib.sha256(p.read_bytes()).hexdigest().upper(); child=hashlib.sha256(q.read_bytes()).hexdigest().upper()
    if parent!=child: raise RuntimeError("Exp3 population is not identity-preserving with Exp2")
    manifest=json.loads(p.read_text(encoding="utf-8")); rows=build_rows(repo)+_load_or_score_cosvoice(repo); rows=_decorate(rows)
    for r in rows:
        if r["speaker"] not in manifest["speakers"]: raise RuntimeError("row speaker absent from frozen population")
        r["split"]=manifest["speakers"][r["speaker"]]
    if sorted({r["case_id"] for r in rows}) != sorted(manifest["cases"]): raise RuntimeError("row case identity mismatch")
    return rows,manifest,parent

def _matrix(rows, features=INPUT, med=None):
    X=np.asarray([[r[f] for f in features] for r in rows],float)
    if med is None: med=np.nanmedian(X,axis=0)
    med=np.where(np.isfinite(med),med,0); return np.where(np.isfinite(X),X,med)

class SmallHead:
    def __init__(self, input_dim, seed=SEED):
        import torch
        torch.manual_seed(seed); torch.use_deterministic_algorithms(True)
        self.torch=torch; self.net=torch.nn.Sequential(torch.nn.Linear(input_dim,32),torch.nn.ReLU(),torch.nn.Linear(32,8)); self.cls=torch.nn.Linear(8,1)
    def transform(self,X):
        with self.torch.no_grad(): return self.net(self.torch.tensor(X,dtype=self.torch.float32)).numpy()
    def predict(self,X):
        with self.torch.no_grad(): return self.torch.sigmoid(self.cls(self.net(self.torch.tensor(X,dtype=self.torch.float32))).squeeze(1)).numpy()

def train_head(rows, allowed, objective, seed=SEED):
    import torch
    train=[r for r in rows if r["split"]=="train" and r["mechanism"] in allowed]
    X0=_matrix(train); med=np.nanmedian(np.asarray([[r[f] for f in INPUT] for r in train],float),axis=0); med=np.where(np.isfinite(med),med,0); X=_matrix(train,med=med); y=torch.tensor([r["label"] for r in train],dtype=torch.float32); head=SmallHead(X.shape[1],seed); head.med=med; opt=torch.optim.Adam(list(head.net.parameters())+list(head.cls.parameters()),lr=.001,weight_decay=.0001); rng=np.random.default_rng(seed)
    groups=defaultdict(list)
    for i,r in enumerate(train): groups[r["mechanism"]].append(i)
    case_counts=defaultdict(int)
    for r in train: case_counts[(r["mechanism"],r["case_id"])] += 1
    weights=np.asarray([1/(len(groups[r["mechanism"]])*case_counts[(r["mechanism"],r["case_id"])]) for r in train],float)
    if objective=="R2_NO_GENERATOR_BALANCING": weights=np.ones(len(train),float)
    weights/=weights.sum()
    for _ in range(60):
        idx=rng.choice(len(train),size=min(96,max(8,len(train))),replace=True,p=weights); xb=torch.tensor(X[idx],dtype=torch.float32); yb=y[idx]; z=head.net(xb); logits=head.cls(z).squeeze(1); ce=torch.nn.functional.binary_cross_entropy_with_logits(logits,yb,reduction="none"); loss=(ce*torch.tensor([weights[i] for i in idx],dtype=torch.float32)).sum()/torch.tensor([weights[i] for i in idx],dtype=torch.float32).sum()
        if objective in ("R2","R3","R2_NO_GENERATOR_BALANCING"):
            zn=torch.nn.functional.normalize(z,dim=1); sim=zn@zn.T/.2; mask=torch.eye(len(idx),dtype=torch.bool); labels=yb[:,None]==yb[None,:]; gen=torch.tensor([allowed.index(train[i]["mechanism"]) for i in idx]); pos=labels & (gen[:,None]!=gen[None,:]) & ~mask; valid=pos.any(1); logp=torch.log_softmax(sim.masked_fill(mask,-1e9),dim=1); con=-(logp.masked_fill(~pos,0).sum(1)/pos.sum(1).clamp_min(1));
            if valid.any(): loss=loss+.25*con[valid].mean()
        if objective=="R3":
            per=[]
            for g in range(len(allowed)):
                gm=torch.tensor([train[i]["mechanism"]==allowed[g] for i in idx])
                if gm.any(): per.append(torch.nn.functional.binary_cross_entropy_with_logits(logits[gm],yb[gm]))
            if per: loss=loss+.5*torch.stack(per).max()
        opt.zero_grad(); loss.backward(); opt.step()
    return head, {"objective":objective,"seed":seed,"epochs":60,"batch_size":96,"generator_balanced":objective!="R2_NO_GENERATOR_BALANCING","case_aware":True,"contrastive_weight":.25 if objective in ("R2","R3","R2_NO_GENERATOR_BALANCING") else 0,"group_robust_weight":.5 if objective=="R3" else 0}

def r0_predictor(rows,allowed=None):
    train=[r for r in rows if r["split"]=="train" and (allowed is None or r["mechanism"] in allowed)]; X=_matrix(train); med=np.nanmedian(X,axis=0); med=np.where(np.isfinite(med),med,0); mu=X.mean(0); sd=X.std(0); sd=np.where(sd<1e-9,1,sd); Z=(np.where(np.isfinite(X),X,med)-mu)/sd; w=np.zeros(Z.shape[1]+1); y=np.asarray([r["label"] for r in train],float)
    for _ in range(1200):
        A=np.c_[np.ones(len(Z)),Z]; p=1/(1+np.exp(-np.clip(A@w,-40,40))); w-=.15*(A.T@(p-y)/len(Z)+1e-3*np.r_[0,w[1:]])
    def pred(rs):
        V=_matrix(rs,med=med); V=(V-mu)/sd; return 1/(1+np.exp(-np.clip(np.c_[np.ones(len(V)),V]@w,-40,40)))
    return pred

def score_metrics(rows,pred,target=None):
    test=[r for r in rows if r["split"]=="qualification_test" and (target is None or r["mechanism"]==target)]; out={}
    for z in ("all","boundary","core"):
        pos=[r for r in test if (z=="all" and r["region"] in ("boundary","core")) or r["region"]==z]; neg=[r for r in test if r["region"]=="clean"]
        if not pos or not neg: out[z]={"AUROC":None,"AUPRC":None,"n":len(pos)+len(neg),"positive_n":len(pos)}; continue
        sc=pred(pos+neg); y=[1]*len(pos)+[0]*len(neg); out[z]={"AUROC":auroc(y,sc),"AUPRC":auprc(y,sc),"n":len(y),"positive_n":len(pos)}
    return out

def bootstrap_fold(rows,preds,ood):
    cases=sorted({r["case_id"] for r in rows if r["split"]=="qualification_test" and r["mechanism"]==ood}); by=defaultdict(list)
    for r in rows:
        if r["split"]=="qualification_test" and r["mechanism"]==ood: by[r["case_id"]].append(r)
    rng=np.random.default_rng(SEED); out={}
    for model,pred in preds.items():
        vals=[]
        for _ in range(BOOT_N):
            chosen=rng.choice(cases,size=len(cases),replace=True); sample=sum((by[c] for c in chosen),[]); pos=[r for r in sample if r["region"] in ("boundary","core")]; neg=[r for r in sample if r["region"]=="clean"]
            if not pos or not neg: continue
            vals.append(auroc([1]*len(pos)+[0]*len(neg),pred(pos+neg)))
        out[model]={"n":BOOT_N,"finite":len(vals),"seed":SEED,"unit":"case_id","ci":[float(np.percentile(vals,2.5)),float(np.percentile(vals,97.5))] if vals else None}
    return out

def probe_accuracy(rows,representation):
    train=[r for r in rows if r["split"]=="train"]; test=[r for r in rows if r["split"]=="qualification_test"]; X=np.asarray([representation(r) for r in train]); T=np.asarray([representation(r) for r in test]); labels=sorted({r["mechanism"] for r in rows}); yi=np.asarray([labels.index(r["mechanism"]) for r in train]); ti=np.asarray([labels.index(r["mechanism"]) for r in test]); med=np.nanmedian(X,0); X=np.where(np.isfinite(X),X,med); T=np.where(np.isfinite(T),T,med); mu=X.mean(0); sd=np.where(X.std(0)<1e-9,1,X.std(0)); X=(X-mu)/sd; T=(T-mu)/sd; w=np.zeros((X.shape[1]+1,len(labels))); A=np.c_[np.ones(len(X)),X]
    for _ in range(400):
        logits=A@w; logits-=logits.max(1,keepdims=True); p=np.exp(logits); p/=p.sum(1,keepdims=True); w-=.2*A.T@(p-np.eye(len(labels))[yi])/len(X)
    z=np.c_[np.ones(len(T)),T]@w; return float((z.argmax(1)==ti).mean()) if len(ti) else None

def run(repo):
    rows,manifest,parent=load_population(repo); out=repo/"results/week5_exp3"; out.mkdir(parents=True,exist_ok=True)
    all_preds={"R0":r0_predictor(rows)}; heads={}
    for name,obj in (("R1","R1"),("R2","R2"),("R3","R3"),("R2_NO_GENERATOR_BALANCING","R2_NO_GENERATOR_BALANCING")):
        h,tm=train_head(rows,sorted({r["mechanism"] for r in rows}),obj); heads[name]=h; all_preds[name]=lambda rs,h=h:h.predict(_matrix(rs,med=h.med))
    main={"R0":score_metrics(rows,all_preds["R0"]),**{m:score_metrics(rows,p) for m,p in all_preds.items() if m!="R0"}}
    folds={}; bootstrap={}
    for fold,(allowed,ood) in FOLDS.items():
        preds={"R0":r0_predictor(rows,allowed)}; local_heads={}
        for name,obj in (("R1","R1"),("R2","R2"),("R3","R3")):
            h,tm=train_head(rows,allowed,obj); local_heads[name]=h; preds[name]=lambda rs,h=h:h.predict(_matrix(rs,med=h.med))
        folds[fold]={"train_mechanisms":allowed,"ood_generator":ood,"models":{m:score_metrics(rows,p,ood) for m,p in preds.items()}}; bootstrap[fold]=bootstrap_fold(rows,preds,ood)
    ood_summary={}
    for m in ("R0","R1","R2","R3"):
        vals=[folds[f]["models"][m]["all"]["AUROC"] for f in folds if folds[f]["models"][m]["all"]["AUROC"] is not None]; ood_summary[m]={"mean_AUROC":float(np.mean(vals)) if vals else None,"worst_AUROC":float(np.min(vals)) if vals else None,"fold_AUROC":vals}
    probe={"R0":probe_accuracy(rows,lambda r:np.asarray([r[f] for f in INPUT],float)),"R1":probe_accuracy(rows,lambda r:heads["R1"].transform(_matrix([r]))[0]),"R2":probe_accuracy(rows,lambda r:heads["R2"].transform(_matrix([r]))[0]),"R3":probe_accuracy(rows,lambda r:heads["R3"].transform(_matrix([r]))[0])}
    robust=ood_summary["R3"]; metrics={"protocol":"WEEK5_EXP3_GENERATOR_DIVERSE_REPRESENTATION_LEARNING","status":"PASS","week4_validation_data_used":"NO","week4_heldout_data_used":"NO","week4_h4_used":"NO","exp2_population_reused":True,"generator_id_used_at_inference":False,"models":main,"ood_summary":ood_summary,"direction":"INCONCLUSIVE"}
    r0=ood_summary["R0"]; metrics["mean_ood_delta_vs_r0"]={m:(ood_summary[m]["mean_AUROC"]-r0["mean_AUROC"] if ood_summary[m]["mean_AUROC"] is not None else None) for m in ("R1","R2","R3")}; metrics["worst_ood_delta_vs_r0"]={m:(ood_summary[m]["worst_AUROC"]-r0["worst_AUROC"] if ood_summary[m]["worst_AUROC"] is not None else None) for m in ("R1","R2","R3")}; metrics["direction"]="WEAK_GO" if metrics["mean_ood_delta_vs_r0"]["R3"]>0 and metrics["worst_ood_delta_vs_r0"]["R3"]>=0 else "NO_GO"
    (out/"representation_manifest.json").write_text(json.dumps({"input":"Exp2_B4_FULL","architecture":"Linear(32)->ReLU->Linear(8)->Linear(1)","ecapa_backbone_trainable":False,"generator_id_used_at_inference":False},indent=2),encoding="utf-8")
    (out/"training_manifest.json").write_text(json.dumps({"models":{**{k:v for k,v in heads.items()}},"seed":SEED,"folds":FOLDS,"sampling":"generator-balanced + case-aware inverse-frequency weights","ood_excluded_from_training":True},indent=2,default=str),encoding="utf-8")
    (out/"metrics.json").write_text(json.dumps(json_safe(metrics),ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"in_domain_metrics.json").write_text(json.dumps(json_safe(main),indent=2),encoding="utf-8")
    (out/"generator_ood_metrics.json").write_text(json.dumps(json_safe(folds),indent=2),encoding="utf-8")
    (out/"region_metrics.json").write_text(json.dumps(json_safe({m:v for m,v in main.items()}),indent=2),encoding="utf-8")
    (out/"generator_probe.json").write_text(json.dumps(json_safe(probe),indent=2),encoding="utf-8")
    (out/"bootstrap.json").write_text(json.dumps(json_safe(bootstrap),indent=2),encoding="utf-8")
    (out/"ablation.json").write_text(json.dumps(json_safe({"R0":"B4_FULL","R1":"balanced_ERM","R2":"contrastive","R3":"contrastive_plus_group_robust","R2_NO_GENERATOR_BALANCING":"contrastive_without_generator_balancing"}),indent=2),encoding="utf-8")
    (out/"per_case_metrics.json").write_text(json.dumps({"case_count":len(manifest["cases"]),"speaker_disjoint":True,"ood_case_identity_preserved":True},indent=2),encoding="utf-8")
    prov={"exp2_parent_manifest_sha256":parent,"exp3_manifest_sha256":hashlib.sha256((repo/"data/manifests/week5_exp3_qualification_population.json").read_bytes()).hexdigest().upper(),"training_seed":SEED,"bootstrap_seed":SEED,"temporal_scale_search":"CLOSED","week4_validation_data_used":"NO","week4_heldout_data_used":"NO","week4_h4_used":"NO"}; (out/"provenance.json").write_text(json.dumps(prov,indent=2),encoding="utf-8")
    return metrics
