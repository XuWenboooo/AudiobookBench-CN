你现在继续执行 AudiobookBench-CN：

DAY 6C — Confound Controls for Speaker-Consistency Localization

==================================================  
0\. Canonical Repository / Workspace
====================================

唯一主仓库：

F:\项目\申请实验室  TTS项目\AudiobookBench-CN

科研 workspace：

F:\项目\申请实验室  TTS项目

AISHELL-3：

F:\项目\申请实验室  TTS项目\datasets\AISHELL-3

AISHELL-3 原始数据严格只读：

- 不修改
- 不删除
- 不移动
- 不重命名
- 不覆盖

所有 Day 6C 新代码、manifest、control WAV、结果和报告  
只能写入 AudiobookBench-CN 主仓库中的新目录。

==================================================

1. 当前科研状态  
   ==================================================

已经完成：

Day 1      PASS  
Day 2      PASS  
Day 3      PASS  
Day 3.5    PASS  
Day 4      PASS  
Day 4.5    PASS  
Day 5      PASS  
Day 6A     PASS（实验管线 PASS；B0 科学结果 NEGATIVE）  
Day 6B     PASS（speaker-consistency signal POSITIVE）

当前冻结数据基础：

- 12 speakers
- train / val / test = 6 / 3 / 3 speakers
- 480 AISHELL-3 utterances
- 24 constructed clean long-form sequences
- 23 paired attack cases
- 23 A0
- 23 A1
- speaker-disjoint
- cross-split leakage = 0

A0：  
cross_speaker_splice

A1：  
artifact_controlled_cross_speaker_splice

A2：  
same_text_tts_replacement = PENDING

constructed long-form != native audiobook

==================================================  
2\. Day 6B 当前核心结果
=================

真实 pretrained speaker backend：

SpeechBrain ECAPA-TDNN  
speechbrain/spkrec-ecapa-voxceleb  
VoxCeleb pretrained  
inference-only  
16 kHz  
192-d

测试环境：

speechbrain 1.1.1  
torch 2.14.0+cpu

speaker temporal grids：

S1:  
1.0 s window  
0.25 s hop

S2:  
1.5 s window  
0.25 s hop

当前主要 baselines：

B0  
Day 6A global train-clean robust-z  
FROZEN / NEGATIVE

B1a  
sequence-local untrimmed speaker prototype  
DEPLOYABLE SETTING

B1b  
sequence-local 20% trimmed speaker prototype  
DEPLOYABLE SETTING

B2  
neighbor speaker change  
DEPLOYABLE SETTING / NEGATIVE

B3  
paired-clean speaker embedding differential  
ORACLE / DIAGNOSTIC ONLY

B4  
energy-transient boundary diagnostic  
DIAGNOSTIC ONLY

主要 Day 6B 结果：

B1 test AUROC：

S1 ≈ 0.83  
S2 ≈ 0.89–0.90

B3 ORACLE：  
≈ 0.996 AUROC

B2：  
≈ 0.43–0.45

B4：  
≈ 0.36–0.37

zone audit：

outside  
<  
boundary  
<  
strict core

即：

speaker-representation anomaly  
确实进入 replacement core。

但：

AUPRC / F1 仍明显低于 AUROC，  
outside false positives 仍存在。

因此当前最安全 claim 是：

“B1 provides a strong temporal  
speaker-representation inconsistency signal.”

不要声称：

“high-precision deployable localizer 已完成”。

==================================================  
3\. Day 6C 唯一科研目标
=================

Day 6C 不追求更高 AUROC。

今天只做：

CONFOUND CONTROL

回答：

Q1.  
Day 6B 的 speaker-consistency signal  
是否主要由 speaker change 驱动？

Q2.  
如果 speaker 不变，  
只改变：

- utterance
- text
- phonetic content
- local recording context

B1 是否仍然大量报警？

Q3.  
constructed 0.3 s fixed gaps、  
silence-heavy windows、  
utterance transitions

是否制造 outside false positives？

Q4.  
0.75 / 1.5 / 2.5 s 不同 manipulation duration  
的 localization 难度是否明显不同？

Q5.  
Window-level AUROC 很高时，  
case-level localization 是否同样可靠？

今天优先级：

confound isolation

>

ground-truth correctness

>

uncertainty

>

performance

==================================================  
4\. 今天绝对禁止
==========

不要：

- MLP
- RandomForest
- CNN
- Transformer
- supervised detector
- train feature weights
- hyperparameter sweep
- test threshold tuning
- 根据结果调整 split
- 根据结果重新生成 A0/A1
- 改 attack interval
- 挑成功案例
- 删除失败案例
- 重新调 ECAPA
- 重新调 S1/S2
- 重新调 Day6B trim ratio
- 部署 A2 TTS
- unseen-generator claims
- adaptive attacker
- native audiobook claims
- 自动进入 Day 7

==================================================  
5\. 开始前冻结 Day 6B
================

开始任何 Day 6C 实验之前创建：

DAY6B_FREEZE.md

至少对以下内容记录 SHA256：

configs/day6b_speaker_consistency.yaml

DAY6B_PRECHECK.md

DAY6B_SPEAKER_CONSISTENCY_REPORT.md

results/day6b/metrics.json  
results/day6b/speaker_scores.csv  
results/day6b/bootstrap_ci.csv  
results/day6b/paired_analysis.csv  
results/day6b/zone_audit.csv  
results/day6b/run_summary.json  
results/day6b/embedding_backend.json

以及：

本地 ECAPA 模型关键 checkpoint / model files。

记录：

- timestamp
- speechbrain version
- torch version
- model identifier
- embedding dimension
- expected sample rate
- checkpoint SHA256
- 当前 pytest count

Day 6C 不允许覆盖任何 Day 6B 结果。

==================================================  
6\. Day 6B Claim Addendum
=========================

创建：

DAY6B_CLAIM_ADDENDUM.md

只做 claim clarification。

不要改任何 Day 6B 数值。

明确：

1.

当前最安全表述：

“B1 provides a strong temporal  
speaker-representation inconsistency signal.”

而不是：

“a high-precision deployable localizer is solved.”

原因：

AUPRC/F1 仍有限，  
outside false positives 仍存在。

1.

B4 negative 只支持：

“the tested energy-transient cue  
does not explain the B1 result.”

不能支持：

“all possible splice/boundary shortcuts  
have been ruled out.”

==================================================  
7\. Dependency Portability
==========================

检查当前 speaker backend 是否只存在 Agent 私有环境。

不要允许正式代码依赖：

.workbuddy/  
Agent private venv  
个人临时绝对路径

建议新增：

requirements-speaker.txt

至少记录已验证：

speechbrain==1.1.1

torch tested version:  
2.14.0+cpu

如果不适合严格 pin torch CPU build，  
可以清楚记录 tested version 和安装说明。

不要做大规模 packaging 重构。

==================================================  
8\. Control C0：  
Same-Speaker Different-Text Splice
==================================

这是 Day 6C 最重要 control。

建立：

C0_same_speaker_different_text_splice

目标：

speaker 保持不变

但改变：

- source utterance
- text
- phones
- prosody
- local recording context

用它测试：

B1 是否主要响应 speaker change，  
还是对任何局部 utterance replacement 都报警。

==================================================  
9\. C0 Target 必须复用原 paired case
===============================

不要创建新的 target protocol。

对于 Day 4.5 的每个 paired_case：

尽可能完全复用：

- clean_sequence_id
- target source utterance
- target_start_sample
- target_end_sample
- duration tier
- target location
- split

只替换 donor。

C0 donor 必须：

donor_speaker == target_speaker

donor_split == target_split

donor_source_sample_id != target_source_sample_id

优先：

donor_text_id != target_text_id

记录：

same_speaker = true

same_text = true / false

预期通常：

same_text = false

如果没有合法 donor：

整个 control case skip。

不得为了凑样本改变 target interval。

==================================================  
10\. C0 两个 DSP 版本
=================

为了严格对应 A0 / A1：

生成：

C0A:  
same_speaker_direct_splice

对应 A0 风格。

生成：

C0B:  
same_speaker_artifact_controlled_splice

对应 A1 风格：

- 相同 duration matching
- 相同 RMS matching
- 相同 gain clamp
- 相同 25 ms crossfade
- 相同 sample boundary semantics

不得重新调 DSP。

这样比较：

A0 vs C0A

A1 vs C0B

==================================================  
11\. C0 Waveform Integrity
==========================

每个 C0 必须验证：

- donor speaker == target speaker
- donor split == target split
- donor utterance != target utterance
- cross-split leakage = 0
- output duration == clean duration
- sample rate == 16k
- mono
- finite waveform
- attack 外 samples unchanged
- attack 内 samples changed
- target interval 与原 paired case 一致
- clean WAV 未被修改
- AISHELL-3 未被修改

所有 checks 必须 fail-closed。

==================================================  
12\. C0 Lineage Manifest
========================

创建：

data/manifests/day6c_same_speaker_control_manifest.csv

至少包含：

control_case_id  
paired_case_id

clean_sequence_id  
control_sequence_id

control_type

target_source_sample_id  
target_speaker  
target_text_id

donor_source_sample_id  
donor_speaker  
donor_text_id

same_speaker  
same_text

split

target_start_sample  
target_end_sample

attack_start_sample  
attack_end_sample

attack_core_start_sample  
attack_core_end_sample

blend_start_sample  
blend_end_sample

duration_tier

duration_matching_method  
rms_gain  
crossfade_samples

sample_rate  
longform_type

必要 hash / lineage fields。

==================================================  
13\. C0 Donor Assignment
========================

必须 deterministic。

优先延续：

balanced donor assignment

目标：

避免同一 donor utterance 被大量复用。

记录：

donor usage count

尽量：

同一 donor utterance 最大复用 <= 1

如果无法做到：

记录真实复用次数。

不能跨 split。

==================================================  
14\. 完全复用冻结 Day 6B ECAPA
========================

C0 必须使用：

完全相同的 ECAPA backend

完全相同：

S1  
S2

完全相同：

preprocessing

完全相同：

B1a  
B1b  
B2

不得重选模型。

不得重新 tuning。

==================================================  
15\. Cross-Speaker vs Same-Speaker 核心比较
=======================================

分别比较：

A0  
vs  
C0A

A1  
vs  
C0B

同 paired_case  
同 target  
同 duration tier

主要比较：

core speaker anomaly  
boundary speaker anomaly  
outside speaker anomaly

以及：

AUROC  
AUPRC  
F1

FULL  
CORE

S1  
S2

train  
val  
test

==================================================  
16\. Day 6C 解释规则预注册
===================

在读取正式结果前冻结解释逻辑：

CASE A：

Cross-speaker high  
Same-speaker substantially lower

解释：

speaker change  
是 B1 signal 的重要贡献因素。

仍然不能说：

pure speaker identity only。

CASE B：

Cross-speaker 与 same-speaker  
同样高

解释：

B1 大量响应  
utterance/content/context changes。

Day 6B 不能作为 speaker-specific result。

CASE C：

Same-speaker 有 signal，  
但明显低于 cross-speaker

解释：

speaker change contributes strongly，  
但 non-speaker confounds 也有贡献。

不得结果出来后改解释标准。

==================================================  
17\. Control C1：  
Speech-Active Masking
=====================

Day 6B backend sanity 已发现：

digital silence embedding  
finite but speaker-meaningless。

constructed long-form 又包含：

fixed 0.3 s silence gaps。

因此建立：

speech_active_mask

只用于 speaker scoring evaluation。

不修改 waveform。

不重新提 attack。

Mask 必须：

label-agnostic。

可以依据：

Day 5 frozen energy / voicing

或直接 waveform energy。

绝对不能读取：

attack GT  
attack_start/end  
variant label

==================================================  
18\. Speech Mask 参数规则
=====================

只能预注册一个主要 mask rule。

例如：

speaker window 中：

speech-active fraction >= fixed threshold

才进入 speech-active evaluation。

threshold 必须：

在看 Day 6C val/test localization 结果前冻结。

不要 sweep：

0.2  
0.3  
0.4  
0.5  
...

然后选最好。

不要 test-driven tuning。

记录：

mask definition  
threshold  
retained-window percentage

==================================================  
19\. Original 与 Masked 都必须完整报告
==============================

所有核心 B1 结果同时报告：

ORIGINAL

和：

SPEECH-ACTIVE MASKED

不得只显示改善版本。

至少比较：

AUROC  
AUPRC  
F1  
core anomaly  
outside anomaly  
retained window fraction

重点回答：

outside FP 是否下降？

AUPRC/F1 是否改善？

core signal 是否保持？

==================================================  
20\. Control C2：  
Attack Duration Stratification
==============================

沿用 frozen tiers：

0.75 s  
1.5 s  
2.5 s

不得重新分桶。

分别统计：

A0  
A1  
C0A  
C0B（如果存在）

至少：

case count  
AUROC  
AUPRC  
F1  
core anomaly  
outside anomaly

分别：

S1  
S2

重点回答：

0.75 s manipulation  
是否显著更难定位？

注意不要写 significantly，  
除非真的做统计检验。

==================================================  
21\. Temporal Resolution Audit
==============================

按 duration tier 报告：

embedding window duration / attack duration ratio

以及：

每个 attack 平均被多少 speaker windows 覆盖

median positive windows per case

FULL positive windows  
CORE positive windows

帮助解释：

为什么 1.5 s ECAPA window  
可能难以精确定位 0.75 s attack。

==================================================  
22\. Control C3：  
Case-Level Evaluation
=====================

Day 6B 的窗口：

hop = 0.25 s

高度相关。

不能把所有 windows 当成独立科研样本。

对每个：

paired_case_id

计算：

case AUROC  
case AUPRC

median anomaly inside core  
max anomaly inside core

median anomaly outside  
max anomaly outside

global peak localization error

==================================================  
23\. Peak Localization Error
============================

定义：

global highest B1 anomaly window center

与：

attack strict-core center

之间：

absolute time error in seconds

字段：

peak_localization_error_seconds

不要根据 GT 找最近正确峰。

主指标只使用：

GLOBAL TOP-1 PEAK

如果想增加 top-k，  
只能作为 secondary，  
且 k 必须预注册。

默认不需要。

==================================================  
24\. Case-Level Summary
=======================

分别报告：

mean  
median  
IQR

并做：

paired-case-level bootstrap

不能 window bootstrap。

继续：

2000 bootstrap resamples

seed：

20260905

除非已有 frozen bootstrap config 指定其他值，  
则沿用已有值。

==================================================  
25\. Same-Speaker Control Statistical Contrast
==============================================

如果实现成本不高，

对：

cross-speaker  
vs  
same-speaker

的 paired case-level：

core anomaly difference

计算：

bootstrap 95% CI

按 paired_case_id 重采样。

这才允许判断：

差异的不确定性。

不要因为平均值不同就写 statistical significance。

==================================================  
26\. Control C4：  
Clean Transition Audit
======================

不生成新攻击。

用原始 clean constructed sequences。

对每条 clean sequence：

选择 B1 top 3 anomaly peaks

规则固定：

按 anomaly descending  
tie 用时间顺序

然后测量每个 peak 到：

最近 utterance boundary

最近 fixed silence gap

的时间距离。

同时记录：

speech-active / silence-heavy

目的：

解释 outside false positives。

==================================================  
27\. C4 只能解释，不能修 test
=====================

C4 是：

ERROR ANALYSIS ONLY。

不能根据：

已知 utterance boundary

去删除 test anomalies。

只有 C1 speech-active mask  
允许改变 evaluation window eligibility，

因为它必须：

label-agnostic  
pre-frozen  
不读取 attack GT。

==================================================  
28\. Expanded Boundary Shortcut Claim
=====================================

报告必须明确：

B4 negative 仅说明：

tested log-energy transient diagnostic  
没有解释 B1 success。

不能声称：

all boundary artifacts ruled out。

C0 / C1 / C4  
是在进一步分析 broader confounds。

==================================================  
29\. A2 明确保持 PENDING
====================

今天不要安装：

CosyVoice  
F5-TTS  
其他 TTS

不要生成 same-text synthetic attack。

C0 只控制：

speaker-change factor。

它不能控制：

text confound。

因此：

same-text TTS replacement  
仍然是未来的重要 control。

==================================================  
30\. Failure Cases
==================

自动收集至少：

- same-speaker C0 高 anomaly
- cross-speaker A0/A1 低 anomaly
- 0.75 s attack miss
- high outside false positive
- speech-active masking 后仍存在的 FP
- peak localization error 最大 case
- C0 > cross-speaker 的异常 case

全部保留。

不得人工删除。

==================================================  
31\. Figures
============

自动、确定性生成图。

至少：

Figure A  
同一 paired case：

clean  
A0  
A1  
C0A  
C0B

B1 trajectory + GT

Figure B  
Original B1  
vs  
Speech-active masked

Figure C  
0.75 s difficult case

Figure D  
2.5 s case

Figure E  
clean transition false-positive case

不得只挑最好看的成功例。

selection rule 写进 config。

==================================================  
32\. Output Structure
=====================

建议：

results/day6c/

├── config.yaml  
├── day6b_freeze_record.json  
├── c0_control_manifest.csv  
├── c0_waveform_verification.csv  
├── c0_output_hashes.csv  
├── speaker_scores_c0.csv  
├── cross_vs_same_speaker.csv  
├── speech_active_mask.csv  
├── original_vs_masked_metrics.csv  
├── duration_stratified_metrics.csv  
├── duration_resolution_audit.csv  
├── case_level_metrics.csv  
├── peak_localization_errors.csv  
├── bootstrap_ci.csv  
├── clean_transition_audit.csv  
├── failure_cases.csv  
├── figures/  
└── run_summary.json

不得覆盖：

results/day6b/

==================================================  
33\. Reproducibility
====================

完整 Day 6C 独立重跑至少一次。

验证：

C0 manifest  
C0 waveform hashes  
C0 speaker embeddings  
speaker scores  
speech mask  
masked metrics  
duration metrics  
case-level metrics  
bootstrap results

如果 backend 可 deterministic：

hash identical。

如果不能：

记录 tolerance。

不要伪造 byte-identical。

==================================================  
34\. Tests
==========

当前基线：

130 passed / 0 failed

所有旧测试必须保留。

新增至少覆盖：

1. Day6B freeze hash verification
2. ECAPA checkpoint hash recorded
3. C0 donor same speaker
4. C0 donor same split
5. C0 donor != target utterance
6. C0 target interval == original paired target
7. C0 output duration unchanged
8. C0 attack outside unchanged
9. C0 attack inside changed
10. C0 A0-style DSP correct
11. C0 A1-style DSP correct
12. C0 donor selection deterministic
13. cross-split leakage == 0
14. Day6B ECAPA config unchanged
15. Day6B S1/S2 unchanged
16. speech mask label-agnostic
17. speech mask does not read GT
18. speech mask deterministic
19. original/masked common-window score identical
20. duration tiers immutable
21. duration stratification counts correct
22. case-level grouping by paired_case_id
23. bootstrap not window-level
24. bootstrap deterministic
25. peak-error correct
26. clean-transition top-3 deterministic
27. Day6B results unchanged
28. Day6A results unchanged
29. earlier frozen hashes unchanged
30. raw AISHELL-3 unchanged

不得删除旧测试。

==================================================  
35\. Research Integrity
=======================

报告必须明确：

- Day 6C 是 confound-control study
- 不是新的 benchmark
- constructed long-form != native audiobook
- C0 controls speaker change but not text/content change
- C0 is not TTS
- A2 same-text TTS remains PENDING
- speech masking is label-agnostic
- ECAPA is VoxCeleb-pretrained, not Mandarin-specific training
- B1 is speaker-representation consistency, not a pure speaker-identity oracle
- high AUROC != high precision localization
- AUPRC / F1 / peak error 必须一起看
- val/test 只有 6 paired cases each
- window observations are correlated
- case-level CI is primary uncertainty analysis
- findings currently apply only to the cross-speaker splice threat model

==================================================  
36\. Day 6C Gate
================

# DAY 6C CONFOUND CONTROL GATE

PASS / FAIL

PASS 表示：

实验正确、可复现、控制问题被回答。

PASS 不要求结果支持 Day6B。

如果 C0 结果推翻 Day6B 的 speaker-specific interpretation：

仍然 PASS，  
但必须如实报告。

PASS 至少要求：

1. Day6B frozen
2. C0 controls generated correctly
3. C0 waveform verification PASS
4. same-speaker donor integrity PASS
5. cross-split leakage = 0
6. cross-vs-same comparison completed
7. speech-active mask completed
8. original + masked both reported
9. duration stratification completed
10. case-level evaluation completed
11. peak-error completed
12. clean-transition audit completed
13. paired-case bootstrap completed
14. failure cases retained
15. reproducibility PASS
16. pytest all pass
17. previous frozen artifacts unchanged

==================================================  
37\. 科学问题必须逐条回答
===============

最终报告必须直接回答：

Q1.

Cross-speaker B1 anomaly  
是否明显高于  
same-speaker C0？

Q2.

Same-speaker C0 还有多少 residual signal？

Q3.

Speech-active masking  
是否降低 outside false positives？

Q4.

Speech-active masking 后：

AUROC  
AUPRC  
F1  
分别怎么变？

Q5.

0.75 / 1.5 / 2.5 s  
哪一档最难？

Q6.

S1 vs S2  
在短攻击上有什么 resolution trade-off？

Q7.

Window-level AUROC  
与 case-level localization  
是否给出一致故事？

Q8.

Global top-1 peak  
通常距离 manipulation core 多远？

Q9.

clean false-positive peaks  
是否集中在 utterance/gap transitions？

Q10.

经过 Day6C 后，  
Day6B 最安全 claim 是什么？

==================================================  
38\. Report
===========

创建：

DAY6C_CONFOUND_CONTROL_REPORT.md

至少：

## 1. Executive Summary

## 2. Day6B Freeze

## 3. Research Questions

## 4. Same-Speaker C0 Protocol

## 5. C0 Integrity

## 6. Cross-Speaker vs Same-Speaker Results

## 7. Speaker-Change Contribution

## 8. Speech-Active Masking

## 9. Original vs Masked Localization

## 10. Attack-Duration Stratification

## 11. Temporal Resolution Analysis

## 12. Case-Level Evaluation

## 13. Peak Localization Error

## 14. Clean Transition Audit

## 15. Bootstrap Uncertainty

## 16. Failure Cases

## 17. Figures

## 18. Reproducibility

## 19. Tests

## 20. Claim Audit

## 21. Research Integrity

## 22. Limitations

## 23. Day6C Gate

PASS / FAIL

## 24. Implications for Next Stage

不要实现下一阶段。

==================================================  
39\. 最终回复格式
===========

任务完成后只回复：

1. Day6B freeze：PASS / FAIL
2. C0 controls：  
   生成多少 C0A / C0B
3. C0 waveform verification：  
   PASS / FAIL
4. Same-speaker donor integrity：  
   PASS / FAIL
5. Cross-split leakage：  
   数值
6. Cross-speaker B1 core anomaly：  
   A0 / A1
7. Same-speaker C0 core anomaly：  
   C0A / C0B
8. Cross-vs-same speaker 差值摘要
9. C0 localization：  
   AUROC / AUPRC / F1
10. Speech-active retained-window 比例
11. Original vs masked：  
    AUROC / AUPRC / F1
12. Outside false-positive change
13. Duration stratification：  
    0.75 / 1.5 / 2.5 s 摘要
14. Case-level median AUROC / AUPRC
15. Global peak localization error：  
    median / IQR
16. Clean transition audit 摘要
17. Bootstrap CI 摘要
18. Failure cases 数
19. Reproducibility：  
    PASS / FAIL
20. pytest：  
    passed / failed
21. Previous hashes：  
    UNCHANGED / CHANGED
22. Day6C Gate：  
    PASS / FAIL
23. Day6B 经过 confound controls 后  
    最安全的科研 claim
24. 修改/新增文件
25. DAY6C_CONFOUND_CONTROL_REPORT.md 路径

不要进入 supervised detector。  
不要进入 A2。  
不要进入 Day7。
