# AudiobookBench-CN：8 周科研计划（刘哲理优先版）

> **主研究主题：** Trustworthy Temporal Security and Forensics for Long-form Generative Speech  
> **中文定位：** 面向长文本生成式语音的时序安全、开放环境泛化与取证评测  
> **第一优先目标实验室：** 刘哲理团队 / 数据与智能系统安全方向  
> **第二优先目标实验室：** 秦勇团队 / 智能语音与生成式语音评测方向  
> **建议周期：** 8 周  
> **建议投入：** 每周 15–25 小时

---

# 一、总原则：一核两翼，但安全主线优先

本项目不再把 “TTS 评测” 作为唯一中心，而是将已有的 temporal reliability 框架进一步安全化。

```text
                       AudiobookBench-CN
                              │
                              ↓
                  Long-form Generative Speech
                              │
                              ↓
                     Temporal Representation
                              │
          ┌───────────────────┼───────────────────┐
          ↓                   ↓                   ↓
 Speaker Trajectory    Prosody Trajectory    Failure Events
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                              ↓
                ┌─────────────┴─────────────┐
                │                           │
                ↓                           ↓
       PRIMARY TRACK                 SECONDARY TRACK
       Security & Forensics          Responsible Evaluation
       （刘哲理优先）                    （秦勇次位）
                │                           │
      Detection / Localization         Human Alignment
      Unseen / Adaptive Attack         Evaluator Reliability
      Attribution / Traceback          Uncertainty / Calibration
      Open-world Robustness            Long-form TTS Evaluation
```

## 项目核心不是

```text
“多做几个 TTS 指标”
```

也不是

```text
“训练一个 Fake / Real 分类器”
```

而是：

> **研究 long-form generative speech 中的局部异常、未知生成器和自适应操纵能否被 temporal signals 检测、定位、归因，并进一步验证这些 temporal evaluator 是否可信。**

---

# 二、研究优先级

## Priority 1 — 刘哲理方向：Temporal Security & Forensics

这是 8 周计划的主线，占总精力约 **65–70%**。

重点问题：

1. **Detection**：是否存在局部 synthetic manipulation？
2. **Localization**：异常具体发生在哪一段？
3. **Generalization**：能否泛化到 unseen generator / unseen manipulation？
4. **Attribution / Forensics**：哪一段、哪类生成过程最可能负责异常？
5. **Adaptive Attack**：攻击者知道 detector 后，能否规避？
6. **Robustness**：channel / noise / codec 后是否仍然可靠？

---

## Priority 2 — 秦勇方向：Temporal Responsible Evaluation

作为共享方法学和第二研究分支，占总精力约 **30–35%**。

重点问题：

1. temporal metric 是否真的反映人类感知？
2. 不同 speaker / prosody evaluator 是否一致？
3. natural speech control 下是否也存在类似 drift？
4. evaluator 在 OOD 条件下是否应该拒绝给出强结论？
5. scalar evaluation 是否掩盖 long-form temporal failure？

这部分不是为了“贴关键词”，而是用于保证 Security Track 的测量基础可信。

---

# 三、核心 Research Questions

## Security-RQ1 — Localized Manipulation Detection

> **Can temporal reliability signals reveal localized synthetic manipulation in long-form speech?**

研究对象：

- TTS segment replacement
- Voice conversion segment replacement
- splice / insert
- generator switching
- speaker switching

基础输出：

```text
Long-form audio
      ↓
Temporal signal
      ↓
Anomaly score
      ↓
Manipulated / Clean
```

但 classification 只能作为 baseline。

---

## Security-RQ2 — Localization and Forensics

> **Can we identify which temporal segments are responsible for abnormal long-form speech behavior?**

目标输出：

```text
00:00 ───────────────────────────── 20:00
              ↑↑↑
         suspicious region
```

而不是只给：

```text
Fake / Real
```

需要研究：

- segment anomaly score
- localization precision / recall
- temporal IoU
- false alarm duration
- responsibility score

---

## Security-RQ3 — Open-world Generalization

> **Do temporal security signals generalize to unseen generators and unseen manipulation strategies?**

典型 protocol：

```text
Train:
Generator A + Generator B
        ↓
Test:
Unseen Generator C
```

以及：

```text
Train:
TTS replacement
        ↓
Test:
VC / splice / unseen manipulation
```

重点不是 closed-set accuracy，而是：

> **cross-generator / cross-attack generalization**

---

## Security-RQ4 — Adaptive Evasion

> **Can an attacker preserve temporal speaker/prosody statistics while injecting manipulated speech?**

构造一个轻量级 adaptive threat model：

```text
Fake candidate
    ↓
match speaker representation
+
match F0 / energy / rate
+
minimize temporal anomaly score
    ↓
attempt to evade detector
```

重点研究：

- detector degradation
- attack success rate
- defense recovery
- feature dependency

---

## Eval-RQ1 — Evaluator Validity

> **Are temporal speaker and prosody signals perceptually meaningful and evaluator-independent?**

检查：

- natural speech control
- two or more speaker evaluators
- multi-dimensional prosody metrics
- small-scale human validation

---

## Eval-RQ2 — Uncertainty and Selective Evaluation

> **When should a temporal evaluator refuse to make a confident claim?**

加入：

- evaluator disagreement
- confidence / uncertainty
- OOD flag
- selective evaluation / reject option

目标不是让 evaluator 在所有样本上都强行输出结论。

---

# 四、8 周总计划

| 周 | 第一优先目标 | 第二优先目标 | 周末必须得到的成果 |
|---|---|---|---|
| **Week 1** | 🧱 Real Pipeline + Threat Model | Evaluator sanity check | **真实数据管线 + 安全实验协议 + 可重复 baseline** |
| **Week 2** | 🧪 Localized Manipulation Benchmark | Natural-speech control | **第一套 controlled manipulation 数据 + temporal feature baseline** |
| **Week 3** | 🎯 Detection → Localization | Multi-evaluator agreement | **不只判 Fake/Real，而是能定位异常区间** |
| **Week 4** | 🌐 Unseen Generator / Unseen Attack | Transferability / uncertainty | **第一组真正的 open-world generalization 结果** |
| **Week 5** | ⚔️ Adaptive Evasion / Attack–Defense | Evaluator dependency analysis | **证明现有 detector 在什么攻击下失效，以及为什么** |
| **Week 6** | 🧭 Attribution / Forensics | Long-form responsible evaluation补强 | **segment responsibility / forensic analysis** |
| **Week 7** | 📊 Final Experiments + Human Validation | 统计与 calibration | **最终实验、bootstrap CI、human check、完整 ablation** |
| **Week 8** | 📄 Security-first Research Package | 秦勇方向副报告 | **同一 Repo + 主安全报告 + 次评测报告** |

---

# 五、详细周计划

## Week 1 — Real Pipeline + Security Threat Model

### 本周唯一目标

先把项目变成：

```text
Real Long-form Audio
        ↓
Controlled Manipulation
        ↓
Temporal Feature Extraction
        ↓
Detection / Localization
        ↓
Evaluation
        ↓
Reproducible Results
```

### 必须完成

- 审计当前代码
- 删除/隔离 mock / random / synthetic-demo claim
- 旧代码进入 `legacy/`
- 建立真实 long-form 数据 manifest
- 建立 natural / synthetic / manipulated 三类 source_type
- VAD / segmentation
- F0 / energy / pause / rate
- 至少两个 speaker evaluator 接口
- 建立 temporal feature format
- 编写正式 threat model
- 确定 train / validation / test 划分原则
- 建立基本 classification + anomaly baseline
- 所有 evaluator / generator / data 版本可追踪

### Threat Model 最低要求

定义攻击者能力：

```text
Attacker can:
- replace local segment
- switch generator
- switch speaker / VC
- apply codec / noise / resampling

Attacker cannot initially:
- modify evaluator internals
- access all hidden test data
```

Week 5 再升级为 adaptive attacker。

### Week 1 Gate

- [ ] 真实音频可读
- [ ] manipulated audio 可生成
- [ ] temporal features 可抽取
- [ ] segment-level labels 可追踪
- [ ] baseline 能跑
- [ ] 结果可复现
- [ ] threat model 写入 `THREAT_MODEL.md`

---

## Week 2 — Localized Manipulation Benchmark

### 核心目标

建立一套小而可信的 controlled manipulation benchmark。

### 操纵类型

至少 3 类：

1. **TTS segment replacement**
2. **Voice / speaker replacement**
3. **Generator switching / synthetic splice**

可选：

- speed / pitch-matched replacement
- boundary-smoothed splice

### 必须保留 Clean Control

每条 manipulated sample 必须有对应 clean source。

结构：

```text
clean_longform/
manipulated/
natural_control/
```

### 数据标签

manifest 增加：

```text
attack_type
attack_start
attack_end
attack_generator
source_generator
source_speaker
replacement_speaker
segment_length
```

### Temporal Signals

共享：

- speaker representation trajectory
- F0 trajectory
- energy trajectory
- pause / rate trajectory
- local change statistics

### Week 2 输出

- controlled manipulation manifest
- clean vs manipulated trajectory figures
- baseline anomaly score
- 第一版 `DATASET_CARD.md`

---

## Week 3 — Detection → Localization

### 核心目标

从：

```text
Fake / Real
```

升级到：

```text
Where is the manipulation?
```

### Baseline 1 — Global Detection

只作为参考：

- Logistic / Linear
- MLP
- simple anomaly threshold

### Baseline 2 — Segment Localization

对每个时间窗输出：

\[
A(t)
\]

并计算：

- segment-level AUROC
- segment-level AUPRC
- temporal IoU
- localization F1
- false alarm duration

### Baseline 3 — Change-point

研究：

- changepoint
- local slope
- max deviation
- local inconsistency

### 秦勇副线同步做

检查：

- Evaluator A vs B
- natural control
- clean TTS
- manipulated TTS

如果异常只在某个 evaluator 上存在，则降低 claim。

### Week 3 输出

至少必须得到：

> **一张时间轴上标出 ground truth manipulation 与 detector anomaly score 的图。**

---

## Week 4 — Unseen Generator / Unseen Attack

### 本周是第一个真正的科研 Gate

重点从 IID 转向：

> **Open-world Security**

### Protocol A — Leave-one-generator-out

```text
Train: A + B
Test : C
```

轮换：

```text
A / B / C
```

### Protocol B — Cross-attack

```text
Train:
TTS replacement

Test:
VC replacement
splice
generator switch
```

### Protocol C — Cross-speaker / Cross-text

必须避免 detector 学到：

- speaker identity
- text identity
- lexical shortcut

### Protocol D — Channel Shift

加入：

- MP3 / AAC
- noise
- reverb
- resampling

### 关键分析

报告：

\[
Performance_{IID}
\rightarrow
Performance_{OOD}
\]

以及：

\[
Localization_{IID}
\rightarrow
Localization_{OOD}
\]

重点不是只找最好数字，而是回答：

> **为什么跨生成器 / 跨攻击时会失败？**

### Week 4 输出

- leave-one-generator-out table
- cross-attack matrix
- IID → OOD degradation
- shortcut / confound audit

---

## Week 5 — Adaptive Evasion / Attack–Defense

### 本周目标

让项目真正进入安全研究，而不是“语音 benchmark + robustness”。

### Adaptive Attacker

攻击者知道我们依赖：

- speaker similarity
- F0
- energy
- speech rate
- local temporal change

于是尝试：

```text
candidate fake segments
        ↓
筛选 / 优化
        ↓
speaker distance 最小
prosody distance 最小
anomaly score 最小
        ↓
插入 long-form speech
```

不需要一开始就做复杂梯度攻击。

可以先做：

- candidate selection attack
- metric matching
- boundary smoothing
- feature-aware search

### 评估

- Attack Success Rate
- Detection drop
- Localization drop
- Evasion rate
- clean false positive
- defense recovery

### Defense

只做轻量级：

- feature ensemble
- multi-evaluator voting
- reject option
- uncertainty-aware detection

不要在 8 周里训练大型 defense model。

### Week 5 输出

必须回答：

> **如果攻击者知道我们在看什么，他能不能绕过去？**

这是 Security Track 最重要的升级。

---

## Week 6 — Attribution / Forensics

### 核心目标

从：

```text
检测异常
```

继续推进到：

```text
解释哪一段最可能负责异常
```

### Segment Responsibility

为每个 segment 定义：

\[
R(t)
\]

可由：

- anomaly magnitude
- counterfactual removal
- local contribution
- evaluator agreement
- temporal consistency change

组成。

### Counterfactual Forensics

例如：

```text
删除 / 替换 segment i
        ↓
global anomaly score 是否恢复？
```

如果恢复明显，则：

```text
segment i responsibility ↑
```

### 可选 Generator Attribution

只作为 forensic 辅助：

> suspicious segment 最可能来自哪类 generator family？

注意：

普通 generator classification 不再是核心创新。

### 秦勇副线同步补强

对 selected samples 做：

- human pairwise check
- speaker consistency judgment
- prosody consistency judgment

用于验证自动 temporal evidence 是否具有感知意义。

### Week 6 输出

- responsibility timeline
- segment ranking
- localization vs attribution 对比
- 典型 forensic case studies

---

## Week 7 — Final Experiments + Human Validation + Statistics

### 冻结协议

从本周开始：

> **不再为了结果修改核心 protocol。**

### 建议规模

资源允许：

- 3–5 generators
- 10–20 speakers
- 100+ sentences / speaker
- 多 attack types
- unseen generator setting
- adaptive setting
- natural control
- channel perturbation

### Human Validation

不做大型 MOS 众测。

只做针对性验证：

- highest anomaly
- lowest anomaly
- evaluator disagreement
- adaptive evasion success
- false positive

评价：

- speaker consistency
- prosody consistency
- perceptual abnormality
- manipulation plausibility

### 统计

至少：

- Mean / Std
- Bootstrap 95% CI
- Effect size
- Paired significance tests
- Pearson / Spearman
- Calibration error（如适用）
- multiple-comparison correction（如需要）

### Week 7 输出

形成完整：

```text
MAIN_RESULTS.md
```

---

## Week 8 — Security-first Research Package

### 主报告：面向刘哲理

建议标题：

# **AudiobookBench-Sec: Temporal Security and Forensics for Long-form Generative Speech**

主要结构：

1. Introduction
2. Threat Model
3. Related Work
4. Benchmark Construction
5. Temporal Security Signals
6. Detection and Localization
7. Open-world Generalization
8. Adaptive Evasion
9. Attribution / Forensics
10. Human Validation
11. Limitations
12. Conclusion

重点关键词：

```text
Generative AI Security
Open-world Detection
Unseen Generator
Adaptive Attack
Localization
Attribution
Forensics
Robustness
```

---

### 副报告：面向秦勇

建议标题：

# **AudiobookBench-Eval: Temporal Responsible Evaluation of Long-form TTS**

重点结构：

1. temporal speaker representation
2. multi-dimensional prosody
3. natural-speech control
4. multi-evaluator agreement
5. human alignment
6. uncertainty / selective evaluation
7. cross-generator transferability

重点关键词：

```text
TTS Evaluation
Long-form Speech
Temporal Consistency
Human Alignment
Evaluator Reliability
Uncertainty
Responsible Evaluation
```

---

# 六、推荐代码结构

```text
AudiobookBench-CN/
│
├── README.md
├── THREAT_MODEL.md
├── DATASET_CARD.md
│
├── configs/
├── data/
│   ├── raw/
│   ├── natural_control/
│   ├── manipulated/
│   └── manifests/
│
├── src/
│   ├── preprocessing/
│   ├── features/
│   ├── evaluators/
│   ├── temporal/
│   ├── security/
│   │   ├── manipulation.py
│   │   ├── anomaly.py
│   │   ├── localization.py
│   │   ├── attribution.py
│   │   └── adaptive_attack.py
│   │
│   ├── evaluation/
│   │   ├── speaker.py
│   │   ├── prosody.py
│   │   ├── uncertainty.py
│   │   └── human_alignment.py
│   │
│   └── statistics/
│
├── experiments/
│   ├── security_track/
│   │   ├── exp01_manipulation/
│   │   ├── exp02_localization/
│   │   ├── exp03_unseen_generator/
│   │   ├── exp04_adaptive_attack/
│   │   └── exp05_forensics/
│   │
│   └── evaluation_track/
│       ├── exp01_natural_control/
│       ├── exp02_multi_evaluator/
│       └── exp03_human_alignment/
│
├── results/
│   ├── security/
│   └── evaluation/
│
├── tests/
└── legacy/
```

---

# 七、Research Gates

## Gate 1 — Week 1

> Pipeline 和 threat model 是否可信？

如果 manipulated data 本身有明显 trivial artifacts，则先修数据，不能继续。

---

## Gate 2 — Week 3

> Temporal signals 是否真的能定位 manipulation？

如果只能做 global classification，不能宣称 temporal forensics。

---

## Gate 3 — Week 4

> IID 有效，OOD 是否仍然有效？

如果 unseen generator 彻底崩溃：

- 保留结果
- 分析 shortcut
- 不为“漂亮结果”调 test set

---

## Gate 4 — Week 5

> Adaptive attacker 是否能明显绕过 detector？

如果能：

- 这是重要结果
- 分析 feature dependency
- 做轻量 defense

如果不能：

- 检查 attack 是否太弱
- 不得直接宣称“robust to adaptive attacks”

---

## Gate 5 — Week 6

> Attribution / responsibility 是否提供比 localization 更多的信息？

如果没有：

- 不强行保留 attribution
- 将其降为 case study

---

## Gate 6 — Week 7

> Automatic evidence 与 human judgment 是否至少方向一致？

如果不一致：

- 缩小 claim
- 把 evaluator reliability 写成核心发现

---

# 八、重要止损线

## 绝对不做

- ❌ 为贴刘哲理而硬加联邦学习 / 差分隐私 / 密码学
- ❌ 把普通 deepfake classifier 包装成 security forensics
- ❌ closed-set accuracy 很高就宣称 open-world robust
- ❌ 一个 evaluator 有效果就宣称真实 speaker drift
- ❌ adaptive attack 太弱却宣称 robust
- ❌ mock / synthetic-demo 支撑正式科研 claim
- ❌ 为显著结果反复修改 test protocol
- ❌ 把 attribution 和 causality 混为一谈
- ❌ 同时训练大型 speech model / LLM judge / complex defense

---

# 九、8 周结束时的最低成功标准

不是必须“做出一个很高准确率模型”。

最低科研成功标准是至少满足以下三项：

1. **构建一套可复现 localized manipulation benchmark**
2. **证明 IID 与 unseen-generator / unseen-attack 条件存在可量化差异**
3. **至少完成 detection → localization 的升级**

理想状态再加入：

4. adaptive evasion
5. responsibility attribution
6. human validation
7. uncertainty / reject option

---

# 十、最终申请叙事

## 面向刘哲理团队

核心一句话：

> **我关注生成式语音在开放环境中的安全失效：不仅判断是否被操纵，还研究局部异常的定位、未知生成器泛化、自适应规避，以及安全事件的时序取证。**

---

## 面向秦勇团队

核心一句话：

> **同一项目的评测层研究长文本 TTS 的 temporal reliability，并验证 speaker / prosody evaluator 的 human alignment、uncertainty 和跨生成器可迁移性。**

---

# 十一、优先级提醒

未来 8 周资源不足时，按以下顺序删减：

```text
必须保留：
Real Data
→ Threat Model
→ Localized Manipulation
→ Detection
→ Localization
→ Unseen Generator

其次：
Adaptive Attack
→ Forensics / Attribution

最后才是：
更多 generator
→ 更多 prosody metric
→ Generator classification
→ 大规模 human study
```

也就是说：

> **宁可完成一个小而严谨的 open-world security study，也不要做一个大而散的 TTS benchmark。**
