# Week 1 Research Retrospective

本文件是对已冻结 Week 1 的科研决策复盘，不是新的实验阶段。它只读取并综合 Week 1 的双重审计、连续性审阅、冻结指标和结果；不修改任何冻结数字或冻结数据。

## 1. Executive Summary

Week 1 的核心产出不是“已经解决了语音取证”，而是建立了一条可复现、可审计、边界清楚的机制验证链：真实 AISHELL-3 → 构造 long-form → 精确局部替换 → 时间特征 → B0 负结果 → ECAPA B1 强信号 → same-speaker 控制 → transition / speech-active 控制。最终状态为 Week 1 Gate PASS、Codex independent audit PASS、Agent continuity review PASS、169 passed / 0 failed、696/696 frozen hashes verified。

最重要的决策含义是：当前最值得继续验证的是“局部 speaker representation consistency 是否在控制 linguistic content 后仍然有效”，而不是立刻训练 classifier 或继续优化 B1 数字。

## 2. What Week 1 Established

以下最多七条，明确区分工程事实与科学发现：

1. **工程事实：真实音频链可复现。** AISHELL-3 原始音频只读使用；12 speakers 按 6/3/3 speaker-disjoint 划分；70 条 Week-1 waveform 在 16 kHz、25 ms/10 ms 网格上产生 224,566 帧；完整测试为 169 passed。该事实证明的是工程可重复性，不是科学创新本身。
2. **工程事实：局部 ground truth 可精确追溯。** 24 条 constructed clean long-form、23 个 paired cases、A0/A1 各 23 条，attack/target/core/blend 的 sample bounds 与秒级时间轴一致，C0 也复用完全相同的目标区间。
3. **科学发现：generic global scalar anomaly fails。** B0 使用 TRAIN CLEAN ONLY 的 robust median/MAD reference；100/250/500 ms 的所有 observed AUROC 均低于 0.5。outside context 比 attack core 更异常，说明全局标量统计不能表达局部 speaker inconsistency。
4. **科学发现：sequence-local pretrained speaker representation 提供强 temporal signal。** 不使用 speaker ID、test enrollment 或 paired clean 的 B1，在 S2/B1b test 上 A0/A1 AUROC 为 0.901421/0.896658；但 AUPRC/F1 明显较低，因此这是强排序信号，不是高精度部署方案。
5. **科学发现：same-speaker control 不产生可用正向 B1 localization。** C0A/C0B 使用 same speaker、same split、different utterance、exact same target interval；S1 core anomaly 约 0.366，而 A0/A1 约 0.729/0.732，C0 test AUROC 约 0.376/0.367。该结果支持当前 protocol 下 cross-speaker substitution 的 specificity。
6. **科学发现：constructed utterance transitions 是主要 outside-FP 来源之一。** 144 个 clean top-three anomaly peaks 的 median boundary distance 为 0.094 s，97.2% 位于 1 s 内；这解释了为什么 AUROC 强于 AUPRC/F1。
7. **科学发现：speech-active control 改变的是 evaluation population。** 固定、label-agnostic 的 speech-active mask 保留多数正例并移除许多 silence/transition-heavy negative windows；masked 结果只能称为 conditional-on-speech-active evaluation，不能写成 detector overall improvement。

## 3. What Week 1 Did Not Establish

以下结论仍 unsupported 或 open：

- native audiobook robustness；
- TTS/deepfake robustness，尤其是 same-text replacement；
- unseen-generator robustness；
- adaptive attacker robustness；
- channel / codec / recording-condition robustness；
- human perceptual realism；
- high-precision deployment readiness；
- pure speaker-identity causality；
- source attribution、generator attribution 或责任归因；
- universal speech forensics。

Week 1 的 A0/A1 与 C0 donor 都涉及 different utterance / different text，因此不能把 observed difference 直接归因于纯 speaker identity。

## 4. Day6A → Day6B → Day6C Scientific Chain

### Day 6A：为什么失败

B0 对每个窗口的 energy、RMS、F0、pause 等标量做全局 robust deviation。该 reference 只来自 train-clean，因而没有 test leakage；但“偏离全局 clean 分布”与“局部 speaker representation 不一致”不是同一个机制。outside context、utterance transition、局部声学变化可以比 attack core 更偏离全局统计，所以 B0 在 train、val、test 都没有形成正向定位信号。

### Day 6B：为什么成功

B1 将一个 suspect sequence 的 ECAPA embedding 与该 sequence 自身的 prototype 比较，机制上直接对准 speaker-representation consistency。它不需要 speaker ID、不需要 test enrollment，也不需要 paired clean。因而它比 global scalar anomaly 更接近当前 threat model 中的局部 cross-speaker substitution mechanism。成功仍是 bounded：AUPRC/F1 低于 AUROC，outside false positives 很多，不能表述为 deployable localizer solved。

### Day 6C：排除了什么、没有排除什么

C0 保持 clean sequence、target utterance、target interval、duration tier、split 不变，只把 donor 换成 same-speaker、same-split、different utterance。C0 的低 AUROC 和较低 core anomaly 排除了一个直接解释：B1 的正向结果并非任何“换了一段别的真实语音”都同样产生。它支持当前 protocol 下对 cross-speaker substitution 的明显 specificity。

C0 没有排除 linguistic content、phonetic distance、utterance difficulty、channel 或 donor-specific acoustic factors；因此它没有建立 pure speaker identity causality，也没有回答 same-text TTS、unseen generator 或 native long-form 条件。

## 5. Strongest Findings

按科研价值而非最高数字排序：

1. **Paired cross-vs-same contrast。** 23 个 paired cases 使用相同 target/interval 的 A0/A1 与 C0A/C0B，S1 core anomaly 约 0.729/0.732 对 0.366/0.366；S1 的有限 paired contrasts 全部指向 cross-speaker 更高。它比单个 AUROC 更能回答“机制是否具有 specificity”；限制是 donor text 未控制，S2 短 attack 有 strict-core resolution gap。
2. **B0 → B1 的机制转折。** 全局 scalar B0 在所有尺度低于 0.5，而 sequence-local ECAPA B1b 在 S2 达到约 0.90 AUROC。这是从“全局异常”转向“机制对齐 representation consistency”的最清晰证据；限制是 precision、case count 与 constructed setting。
3. **Transition / population controls。** 144 个 clean peaks 靠近构造边界，speech-active mask 保留多数正例并减少 transition-heavy negatives。它把 B1 的强 AUROC 放回真实 evaluation population 中；限制是 masked metrics 不是新 detector，也不是无条件部署指标。

## 6. Weakest Links

- 构造 long-form 不是 native audiobook，utterance transition 是人为可追溯但非自然的边界。
- 23 cases、val/test 各 6 cases，case-level uncertainty 较大。
- C0 只控制 speaker/split/target interval，不控制 text/phonetic content/channel。
- B1 的 AUROC 与 AUPRC/F1 差距说明排序能力不等于高精度定位。
- 0.75 s attack 在 S2 的窗口分辨率不足；部分 strict-core slice 没有 majority-positive window。
- B3 的近乎完美结果是 ORACLE，不能作为可部署证据；B4 只是 DIAGNOSTIC。
- speech-active mask 改变了 prevalence 与 negative population，不能单独比较成“性能提升倍数”。

## 7. Remaining Confounds

1. **Linguistic content confound：** cross-speaker 与 same-speaker donor 都来自不同 utterance；speaker change 与 text/phonetic change 尚未拆开。
2. **Construction confound：** long-form 是 deterministic concatenation，transition、silence 和 boundary statistics 可能不同于 native audiobook。
3. **Acoustic/channel confound：** donor recording condition、loudness、codec、microphone/channel 尚未系统控制。
4. **Duration-resolution confound：** 1.0/1.5 s windows 对 0.75 s attack 的 strict-core majority rule 会产生不可测 slice。
5. **Model provenance confound：** ECAPA 是 VoxCeleb pretrained representation；当前结果证明的是该 representation 在本协议中的信号，不是纯身份因果。
6. **Population confound：** conditional-on-speech-active 只描述保留下来的窗口群体；原始和 masked 必须同时报告。

## 8. Reviewer Attack Surface

| Reviewer question | Current answer | Remaining gap |
|---|---|---|
| “这只是 splice，不是 TTS。” | Correct。Week 1 只声称 controlled real cross-speaker substitution，明确不声称 TTS/deepfake。 | 需要 same-text TTS protocol 才能测试更接近 synthetic replacement 的问题。 |
| “same-speaker control 是否足够？” | C0 保持 target/interval/tier/split，same speaker/split/different utterance，23×2 waveform verification PASS。 | 未控制 text、phonetic distance、channel 和 donor difficulty。 |
| “constructed long-form 是否太人工？” | 是工程构造，不冒充 native audiobook；边界可追溯并被单独审计。 | 需要 native/native-like longer-form validation。 |
| “speaker embedding 是否只是在识别录音条件？” | B1 使用 sequence-local prototype；C0 降低了 arbitrary different-real-speech 的解释。 | 仍未做 channel-matched controls 或 cross-channel stress test。 |
| “为什么 masked evaluation 改了 population？” | 因为 mask 删除 silence/transition-heavy negatives；因此结果标为 conditional-on-speech-active，并保留 unmasked 对照。 | 还需预注册更完整的 population reporting 与外部验证。 |
| “AUROC 0.90 是否意味着可部署？” | 不意味着。AUPRC/F1 较低，outside FP 多，Week 1 明确拒绝 deployment claim。 | 需要更大 case count、precision-oriented protocol 和 calibration。 |
| “B3 近乎完美是否泄漏？” | B3 明确标为 ORACLE ONLY；B1 不读取 paired clean。 | 需要在论文中严格隔离 oracle 与 deployable baselines。 |
| “结果是否只是选了有利的 attack duration / threshold？” | duration tiers、grids、train-only threshold、bootstrap seed 和 frozen hashes 均已冻结。 | 0.75 s resolution limitation 仍需专门 protocol；不能事后调 S1/S2。 |

## 9. Week2 Decision Matrix

| Candidate | Scientific information gain | Liu-style security framing | Implementation cost | Confound risk | Dependency risk | Decisive result potential |
|---|---|---|---|---|---|---|
| A2 same-text TTS replacement | Very high：直接控制 linguistic content | Very high：最接近“局部 synthetic replacement”问题 | High | Medium（仍有 generator/channel confounds） | High：TTS stack/model provenance | High，正负结果都能改变当前解释 |
| Unseen-generator | High：测试 representation generalization | High | Medium–High | Medium–High（generator 与 channel 混合） | Medium–High | High，但解释空间更宽 |
| Short-attack resolution | Medium：澄清当前 window limitation | Medium | Low–Medium | Low | Low | Medium；主要改善可测性而非机制判别 |
| Native long-form | High：外部生态有效性 | Very high | Very high | High（自然边界、channel、content） | Medium | Medium–High，但变量很多 |
| Channel robustness | High：排除录音条件捷径 | High | Medium | Medium | Medium | High，可能推翻或削弱 B1 specificity |

矩阵中的 cost 不是排序主因；排序优先考虑哪个实验最可能改变对当前结论的理解。

## 10. Recommended Week2 Priority

### PRIORITY 1 — A2 same-text TTS replacement（只做 protocol recommendation）

A2 控制 linguistic content / transcript，使 clean 与 replacement 尽量共享同一文本内容，从而直接检验 B1 信号是否仍来自 speaker representation change，而不是 different-text splice。它不控制 generator family、channel、prosody realism、adaptive attacker 或 native audiobook context，因此结果仍需 bounded。

它比现在直接训练 classifier 更有信息价值，因为 classifier 只会把当前 confounds 重新编码，不能回答机制归因；它也比先做 unseen-generator 更合理，因为若 linguistic content 尚未控制，unseen-generator 的失败或成功都难以解释。A2 的代价是 TTS 依赖、provenance 和数据生成流程更复杂，必须先写 protocol、冻结 controls 和 provenance，再决定是否实施。

### PRIORITY 2 — short-attack temporal resolution

专门解决 0.75 s attack 与 1.5 s window 的 majority-core 不可测问题；目标是可测性审计，不是为了让 AUROC 变好。

### PRIORITY 3 — native/native-like longer-form validation

用于检验 constructed transition 结论和 B1 outside-FP 行为能否迁移到更自然的长段语音。该项成本高、confound 多，放在 A2 与 resolution protocol 之后。

## 11. Stop-Doing List

- 不再重复 Week 1 audit，除非出现新的、可复现的科学错误。
- 不继续优化 B1 AUROC 或为结果好看重新选择 grid/threshold。
- 不现在上 supervised classifier。
- 不为了短 attack 事后调 S1/S2 并把变化称为 detector 改进。
- 不把 masked metrics 写成 unconditional detector overall improvement。
- 不把 A0/A1 写成 TTS deepfake。
- 不碰 frozen Week‑1 artifacts、冻结结果或冻结数字。
- 不在没有 protocol、provenance、split 和 control 设计前安装 TTS 或生成新音频。

Week 1 retrospective decision: **PASS；进入 Week 2 protocol design 的建议入口是 A2 same-text TTS replacement，但本文件不启动任何 Week 2 implementation。**
