你现在接管 AudiobookBench-CN 项目的 Day 6A：

Temporal Aggregation + Non-trained Localization Baseline

========================  
唯一主仓库
=====

F:\项目\申请实验室  TTS项目\AudiobookBench-CN

科研 workspace：

F:\项目\申请实验室  TTS项目

AISHELL-3：

F:\项目\申请实验室  TTS项目\datasets\AISHELL-3

原始数据保持只读。

========================  
当前项目状态
======

Day 1 PASS  
Day 2 PASS  
Day 3 PASS  
Day 3.5 PASS  
Day 4 PASS  
Day 4.5 PASS  
Day 5 Engineering PASS

Day 4.5 当前冻结数据：

- 12 speakers
- train / val / test = 6 / 3 / 3 speakers
- 480 utterances
- 24 clean constructed long-form sequences
- 23 paired cases
- 23 A0
- 23 A1
- cross-split leakage = 0
- paired target equality PASS
- paired donor equality PASS
- waveform verification PASS
- deterministic regeneration PASS

Day 5 当前已完成：

- 70 waveforms
  - 24 clean
  - 23 A0
  - 23 A1
- unified grid:
  - 25 ms window
  - 10 ms hop
  - 16 kHz
- total frames = 224,566
- Energy
- Log Energy
- RMS
- Voiced Ratio
- Pause Ratio
- F0
- praat-parselmouth F0 = 70/70
- speaker embedding = BLOCKED
- paired frame alignment PASS 23/23
- attack/core/blend projection PASS
- pytest = 76 passed
- previous frozen hashes unchanged

========================  
必须先阅读
=====

至少阅读：

AUDIT.md  
THREAT_MODEL_v0.md  
DAY3_REAL_DATA_REPORT.md  
DAY35_LONGFORM_PROTOCOL_REPORT.md  
DAY4_MANIPULATION_REPORT.md  
DAY45_EXPANDED_PAIRED_ATTACK_REPORT.md  
DAY5_PRECHECK.md  
DAY5_TEMPORAL_SIGNAL_REPORT.md  
DATASET_CARD.md

以及：

configs/  
src/audiobookbench/temporal/  
src/audiobookbench/security/  
tests/  
results/day5_validation/

不要重新设计数据协议。

========================  
今天唯一目标
======

建立 Day 6A：

Temporal Aggregation  
+  
Non-trained anomaly scoring  
+  
Localization sanity evaluation

今天不要：

- MLP
- Random Forest
- CNN
- Transformer
- supervised classifier
- learned detector
- hyperparameter search
- threshold tuning on test
- unseen-generator claims
- A2 TTS
- speaker embedding substitute
- 自动进入 Day 6B / Day 7

========================  
一、保护已有数据
========

开始前重新验证：

- Day 3 frozen hashes
- Day 3.5 clean hashes
- Day 4 artifacts
- Day 4.5 hashes
- Day 5 feature outputs

不得修改：

- 原始 AISHELL-3
- clean/manipulated WAV
- frozen manifests
- Day 5 raw frame features

Day 6A 新结果写入新目录。

========================  
二、Day 5 原始 10ms grid 保持冻结
=========================

不要修改 Day 5：

25 ms window  
10 ms hop

它是底层 measurement grid。

Day 6A 在其上增加新的：

temporal aggregation layer

而不是重新提特征。

========================  
三、Aggregation Layer
===================

目标：

把过细的 10ms frame signals 聚合为更适合秒级攻击 localization 的时间单元。

第一版固定少量尺度。

建议至少：

100 ms  
250 ms  
500 ms

可以根据实现稳定性只保留其中 2–3 个，  
但必须在 config 中冻结。

建议：

configs/day6a_localization_baseline.yaml

每个 aggregation window 必须明确：

- window duration
- hop duration
- start
- end
- center
- covered Day5 frame indices
- covered sample interval

禁止不同 variant 使用不同时间网格。

同一 paired_case_id 的：

clean  
A0  
A1

聚合网格必须完全一致。

========================  
四、Aggregation Features
======================

只使用 Day 5 已经真实提取的 scalar signals：

- F0
- Energy
- Log Energy
- RMS
- Voiced Ratio
- Pause Ratio

不得引入新模型。

每个 aggregation window 可以计算：

- mean
- std
- median
- min/max（如稳定）
- voiced fraction
- valid-F0 fraction

但避免爆炸式增加特征。

保持：

small  
interpretable  
traceable

F0 的 unvoiced 必须保持语义正确，  
不能用 0 当作真实 pitch 参与普通均值。

========================  
五、建立 Clean Reference
====================

Day 6A 不训练 detector。

需要建立 non-trained reference。

严格避免泄漏：

只能使用 TRAIN CLEAN  
建立 reference/statistics。

val/test clean 或 manipulated  
不得用于估计 reference 参数。

例如可以计算 train-clean：

- global robust median
- MAD
- mean/std（仅在数值稳定时）

对每个 feature 得到：

reference center  
reference scale

scale 必须有 epsilon protection。

所有 reference 参数保存到：

results/day6a/reference/

并记录来源：

TRAIN CLEAN ONLY

========================  
六、第一版 anomaly score
===================

实现最简单、完全非训练的 anomaly baseline。

至少实现：

B0:  
absolute robust z-score

例如对每个 feature：

z_f(t) =  
|x_f(t) - median_train_clean_f|  
/  
(MAD_train_clean_f + eps)

然后构造简单综合：

A(t) =  
mean of valid feature z-scores

或者明确、固定的等权组合。

不要：

学习 feature 权重。

不要：

根据 test 表现选择 feature 权重。

如果某 feature 无效/缺失，  
必须显式处理。

========================  
七、必须做 Feature-specific Scores
=============================

除了 combined anomaly score，  
还必须分别保留：

A_f0(t)  
A_energy(t)  
A_rms(t)  
A_voicing(t)  
A_pause(t)

目的：

后续判断 detector 是否只依赖：

固定 silence gap  
energy jump  
F0 discontinuity

不能只保存一个黑盒总分。

========================  
八、A0 / A1 必须分开
==============

所有结果必须分别报告：

clean  
A0  
A1

不能先合并成：

manipulated

因为 Day 4.5 的核心设计就是 paired A0/A1。

同一 paired_case_id：

必须能够逐时间点比较：

clean  
A0  
A1

========================  
九、Ground Truth Aggregation
==========================

从 Day 5 frame-level ground truth 投影到 Day 6A aggregation window。

每个聚合单元至少记录：

attack_overlap_ratio  
core_overlap_ratio  
blend_overlap_ratio

以及可派生布尔标签：

is_attack_window  
is_core_window  
is_blend_window

布尔阈值必须预先固定。

例如：

overlap_ratio > 0

或者另一个明确规则。

不要根据 performance 调整。

========================  
十、不要马上调 Threshold
=================

第一阶段主要输出连续：

A(t)

不要以 test set 调 anomaly threshold。

如果必须为了 localization F1 做一个 threshold sanity baseline：

只能：

在 TRAIN clean / TRAIN attack 可用信息上确定，  
或者使用固定规则。

然后原样应用到 val/test。

绝对不能：

看 test F1 后调整 threshold。

========================  
十一、Localization Evaluation
==========================

Day 6A 允许计算轻量 evaluation，  
但只针对 non-trained baseline。

至少计算：

1. frame/window-level AUROC
2. frame/window-level AUPRC
3. localization F1

但必须：

train  
val  
test

分别报告。

不能只报告 pooled result。

同时分别报告：

A0  
A1

不要只给总 manipulated。

这和第一周计划的最小指标：  
segment AUROC、segment AUPRC、localization F1  
保持一致。

========================  
十二、Core vs Full Region
======================

必须做两种 ground truth：

GT-FULL:  
attack / blend full changed region

GT-CORE:  
strict attack core

因此至少分别输出：

AUROC_full  
AUPRC_full  
F1_full

AUROC_core  
AUPRC_core  
F1_core

目的是防止 anomaly 只集中在 splice boundary，  
却被误认为检测到了 replacement core。

========================  
十三、Boundary Shortcut Audit
==========================

这是核心科研检查。

分别统计：

outside  
blend boundary  
strict core

中的 anomaly score。

至少报告：

mean  
median

并比较：

A0  
A1

重点回答：

anomaly 高分是否主要集中在 blend / splice boundary，  
而不是 core？

如果是：

必须如实记录。

不要把它包装成 localization success。

========================  
十四、Pause Confound Ablation
==========================

Day 5 已经发现：

constructed long-form 固定 0.3s gap  
可能污染 pause feature。

Day 6A 必须做一个最小 ablation：

Baseline ALL:  
包含 pause/voicing features

Baseline NO_PAUSE:  
移除 pause-related features

比较：

val/test localization metrics。

目的：

判断结果是否主要依赖 fixed-gap shortcut。

不要根据 ablation 结果再回头修改数据。

========================  
十五、Energy Shortcut Ablation
===========================

建议再做：

Baseline NO_ENERGY

去除：

energy  
log_energy  
RMS

保留：

F0  
voicing/pause

如果计算成本不高则必须完成。

这样后续可以判断：

检测是否几乎完全来自 amplitude / splice artifact。

仍然不要做 feature selection。

这些是预定义 ablation。

========================  
十六、Multi-scale Evaluation
=========================

对预先冻结的 aggregation scales：

例如：

100 ms  
250 ms  
500 ms

分别运行同样 baseline。

不要选一个“最好结果”后只报告它。

全部报告。

可以推荐一个后续尺度，  
但必须显示完整结果。

========================  
十七、Paired A0/A1 Analysis
========================

利用 Day 4.5 paired design。

对每个 paired_case_id 比较：

A0 localization  
vs  
A1 localization

同 target  
同 donor  
同 crop

至少输出：

paired delta AUROC（如果定义合理）  
paired delta anomaly inside target  
paired delta anomaly at boundary  
paired delta anomaly in core

核心问题：

artifact control 后，  
anomaly 是否明显下降？

如果下降：

只能说明当前 baseline 对这些 artifact controls 敏感。

不能直接说：

A1 更隐蔽  
或  
A1 更真实。

========================  
十八、Sanity Figures
=================

生成至少：

5 个 paired cases

每个 case 一张 localization figure。

建议显示：

Ground Truth full region  
Ground Truth core  
A0 anomaly  
A1 anomaly  
clean/reference trajectory

以及少量最有解释性的 feature score。

输出目录：

results/day6a/figures/

必须包括：

成功 case  
失败 case

不能只挑最好看的。

选择规则必须确定性。

========================  
十九、Failure Case Collection
==========================

自动保存：

Top failure cases

例如：

- false positive highest
- attack core low-score
- boundary-only detection
- A0 success / A1 failure
- clean high anomaly

生成：

results/day6a/failure_cases.csv

不要人工删除失败样本。

========================  
二十、输出文件
=======

建议生成：

results/day6a/  
├── config.yaml  
├── reference/  
├── aggregated_features.csv  
├── anomaly_scores.csv  
├── metrics.json  
├── metrics_by_split.csv  
├── metrics_by_attack.csv  
├── metrics_by_scale.csv  
├── ablations.csv  
├── paired_analysis.csv  
├── failure_cases.csv  
├── figures/  
└── run_summary.json

========================  
二十一、Tests
=========

当前 baseline：

76 passed

保留所有已有测试。

新增至少覆盖：

1. aggregation grid deterministic
2. clean/A0/A1 aggregation alignment
3. aggregation 不越界
4. train-clean-only reference
5. val/test 不参与 reference estimation
6. robust z-score finite
7. zero-scale protection
8. F0 invalid/unvoiced handling
9. combined anomaly deterministic
10. full GT projection
11. core GT projection
12. blend GT projection
13. threshold 不使用 test
14. A0/A1 paired alignment
15. multi-scale reproducibility
16. pause ablation
17. energy ablation
18. failure-case collection deterministic
19. existing hashes unchanged
20. Day 5 feature files unchanged

不得删除或修改旧测试来换取通过。

========================  
二十二、Research Integrity
======================

必须明确：

- Day 6A 是 non-trained baseline
- anomaly score != learned detector
- constructed long-form != native audiobook
- A0/A1 有 different-text confound
- speaker embedding 尚未实现
- A2 TTS PENDING
- 16 kHz standardized condition
- fixed 0.3s gaps 可能构成 pause shortcut
- high AUROC 不自动意味着成功 localization
- boundary-only response 不能声称检测到了 manipulation core

如果 baseline 很差：

如实报告。

不要改变数据。

不要重新生成攻击。

不要调整 test set。

不要为了漂亮结果调 protocol。

========================  
二十三、Day 6A Gate
===============

最后判断：

DAY 6A NON-TRAINED LOCALIZATION BASELINE  
= PASS / FAIL

这里 PASS 表示：

实验管线可靠运行。

不是表示：

检测性能好。

PASS 至少要求：

1. temporal aggregation 正常
2. train-only reference 正常
3. anomaly score 正常
4. train/val/test 独立评估
5. A0/A1 独立评估
6. full/core ground truth 都能评估
7. pause ablation 完成
8. energy ablation 完成
9. multi-scale 完成
10. failure cases 保留
11. results reproducible
12. pytest 全通过
13. frozen artifacts unchanged

即使 AUROC 接近随机：

只要实验正确，  
Gate 仍然可以 PASS。

========================  
二十四、生成报告
========

创建：

DAY6A_NONTRAINED_LOCALIZATION_REPORT.md

必须包括：

## 1. Executive Summary

## 2. Input Data

## 3. Aggregation Protocol

## 4. Train-clean Reference

## 5. Anomaly Score Definition

## 6. Multi-scale Results

## 7. Train / Val / Test Results

## 8. A0 vs A1 Results

## 9. Full-region vs Core Results

## 10. Pause Ablation

## 11. Energy Ablation

## 12. Boundary Shortcut Audit

## 13. Paired A0/A1 Analysis

## 14. Failure Cases

## 15. Figures

## 16. Reproducibility

## 17. Tests

## 18. Research Integrity

## 19. Limitations

## 20. Day 6A Gate

PASS / FAIL

## 21. Recommendation for Day 6B

不要实现 Day 6B。

========================  
二十五、最后只回复
=========

1. aggregation scales
2. aggregated windows 数
3. reference samples/windows 数
4. anomaly features
5. train/val/test AUROC + AUPRC + F1
6. A0 vs A1 摘要
7. full vs core 摘要
8. pause ablation 摘要
9. energy ablation 摘要
10. boundary shortcut audit 摘要
11. failure cases 数
12. reproducibility PASS/FAIL
13. pytest passed/failed
14. previous hashes unchanged/changed
15. Day 6A Gate PASS/FAIL
16. 修改/新增文件
17. DAY6A_NONTRAINED_LOCALIZATION_REPORT.md 路径

不要进入 Day 6B。
