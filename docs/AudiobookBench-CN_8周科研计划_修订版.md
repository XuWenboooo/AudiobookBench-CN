# AudiobookBench-CN：8 周科研计划（Temporal Reliability 研究版）

> **项目定位：** 面向长文本语音合成的时序可靠性评测基准  
> **英文副标题：** *A Benchmark for Temporal Reliability in Long-form Text-to-Speech*  
> **核心问题：** 传统 utterance-level 评测是否会掩盖长文本 TTS 随生成时间/位置出现的结构性失效？这些失效能否被可信、可重复地测量？  
> **建议周期：** 8 周  
> **建议投入：** 每周 15–25 小时

---

# 一、项目总体研究路线

项目不再把 Speaker Drift、Prosody Drift、Generator Attribution 视作三个彼此并列的独立任务，而是围绕一个主线展开：

> **Temporal Reliability of Long-form TTS**

```text
                         AudiobookBench-CN
                                │
                                ↓
                    Long-form TTS Generation
                                │
                                ↓
                   Temporal Reliability Evaluation
                                │
           ┌────────────────────┼────────────────────┐
           ↓                    ↓                    ↓
   Speaker Trajectory    Prosody Trajectory    Failure Events
           │                    │                    │
           └────────────────────┼────────────────────┘
                                ↓
                      Evaluator Reliability
                                │
                  ┌─────────────┼─────────────┐
                  ↓             ↓             ↓
          Natural Control   Multi-Evaluator   Human Check
                                │
                                ↓
                    Generator Failure Patterns
                                │
                                ↓
                    Robustness / OOD / Real-world
```

这里的关键变化是：

- **Speaker Drift** 不再被直接解释成“身份真的漂移”，而是先称为 **speaker representation drift**。
- **Prosody Drift** 不再用单一 F0 指标代表，而是用多维 trajectory。
- **Generator Attribution** 从核心研究问题降级为附加分析。
- 核心创新点转为：**把质量看成随时间变化的 trajectory，而不是单个 utterance 的 scalar score。**

---

# 二、核心 Research Questions

## RQ1 — Long-horizon Degradation

> **Does synthesis quality change systematically as generation horizon increases?**

研究长文本 TTS 是否随着生成位置、时间或上下文长度增加，出现系统性变化。

核心形式：

\[
M(t)
\]

而不是只得到单个：

\[
M
\]

关注：

\[
\Delta M(t)=M(t)-M(0)
\]

以及：

\[
\frac{dM}{dt}
\]

## RQ2 — What Degrades?

> **Which dimensions exhibit long-horizon degradation: speaker representation, prosody, fluency, or other acoustic characteristics?**

重点研究：

- Speaker representation consistency
- Pitch / F0
- Energy
- Rhythm
- Duration
- Pause
- Speech rate
- Intensity
- Local acoustic failures

目标不是证明“所有指标都会变差”，而是定位：

> **到底是什么在变化。**

## RQ3 — Can We Trust the Measurement?

> **How robust are long-form degradation measurements across evaluators, acoustic conditions, and natural-speech controls?**

必须检查：

- 不同 speaker embedding 模型是否得到一致结论
- 真人长语音是否也存在类似 drift
- channel / noise 是否会制造“假漂移”
- 不同指标之间是否一致
- 是否存在 evaluator artifact

也就是说：

> **不仅评估 TTS，也评估 evaluator 本身是否可信。**

## RQ4 — Are Failure Modes Generator-Specific?

> **Do different TTS generation paradigms exhibit distinct temporal failure patterns?**

比较不同：

- generator
- architecture
- generation paradigm
- streaming / non-streaming
- AR / NAR / flow / diffusion（取决于最终可获取模型）

重点不是单纯比较：

```text
Model A > Model B
```

而是研究：

```text
不同生成范式是否具有不同的 long-horizon failure pattern？
```

---

# 三、8 周总计划

| 周 | 核心目标 | 主要工作 | 周末必须得到的成果 |
|---|---|---|---|
| **Week 1** | 🧱 工程重构 + 真实数据 Pipeline | 清理代码、真实音频、manifest、VAD、F0、speaker embedding、evaluator sanity check | **可信、可重复的真实数据 pipeline** |
| **Week 2** | 🎙️ Speaker Trajectory + Natural Control | 建立 speaker representation trajectory；加入真人长语音 control；至少 2 个 speaker evaluator | **第一组可信 speaker trajectory + control** |
| **Week 3** | 🎵 Prosody Trajectory | F0、energy、rhythm、pause、duration、speech rate、intensity 的多维轨迹 | **第一组多维 prosody trajectory** |
| **Week 4** | 🧪 Evaluator Reliability | 比较不同 evaluator、指标、channel 条件；分析 evaluator dependency | **证明哪些指标可信、哪些可能是假象** |
| **Week 5** | 🔬 Temporal Failure Taxonomy | 区分累积漂移、突发失效、震荡、恢复；changepoint / slope / recovery | **长文本 TTS failure taxonomy** |
| **Week 6** | 🏗️ Generator Architecture + Robustness | 比较不同生成范式；加入 codec/noise/reverb/OOD | **生成器特异 failure pattern + robustness** |
| **Week 7** | 📊 Final Experiment + Human Validation | 扩大数据量、bootstrap CI、effect size、人工核验、最终统计 | **最终实验结果集** |
| **Week 8** | 📄 Paper / Benchmark / GitHub | 收口 benchmark、README、实验报告、图表和复现流程 | **完整研究项目 + 8–12 页报告** |

---

# 四、详细周计划

## Week 1 — 工程重构 + 真实数据 Pipeline

### 核心目标

把当前项目从：

> `代码 Demo / synthetic experiment`

变成：

> **真实音频 → preprocessing → features → evaluation → results**

并且从第一周开始加入：

> **Evaluator Sanity Check**

避免后续出现“指标本身不可靠，但我们把它当成真实现象”的问题。

### 主要任务

- 完整检查现有项目
- 检查所有 import、依赖和缺失文件
- 找出 synthetic / mock / random data
- 保留旧代码到 `legacy/`
- 重构项目目录
- 建立真实数据 manifest
- 实现音频读取
- 实现 VAD
- 实现 F0
- 建立 speaker embedding 接口
- 建立基础 prosody 特征
- 记录 generator / speaker / text / segment metadata
- 建立 reproducibility
- 建立基础测试
- 为至少两个 speaker evaluator 预留统一接口
- 增加 evaluator version / model checkpoint 记录

### 推荐项目结构

```text
AudiobookBench-CN/
│
├── README.md
├── configs/
├── data/
│   ├── raw/
│   ├── manifests/
│   ├── natural_control/
│   └── processed/
│
├── src/
│   ├── preprocessing/
│   ├── features/
│   ├── evaluators/
│   ├── evaluation/
│   └── utils/
│
├── experiments/
│   ├── exp01_speaker_trajectory/
│   ├── exp02_prosody_trajectory/
│   ├── exp03_evaluator_reliability/
│   ├── exp04_failure_taxonomy/
│   └── exp05_generator_robustness/
│
├── results/
│   ├── raw/
│   ├── figures/
│   ├── tables/
│   └── logs/
│
├── tests/
└── legacy/
```

### Week 1 验收

```text
Real Audio
    ↓
Preprocessing
    ↓
Feature Extraction
    ↓
Evaluator Interface
    ↓
Evaluation
    ↓
Results
```

必须完整跑通。

---

## Week 2 — Speaker Trajectory + Natural Speech Control

### 核心问题

> 长文本 TTS 中，speaker representation 是否随生成位置系统性变化？

先使用保守术语：

> **speaker representation drift**

不要直接写：

> speaker identity drift

除非后续 human validation 支持。

### 基础指标

\[
Drift(t)=1-\cos(E_0,E_t)
\]

但必须升级为 trajectory：

\[
D(t)
\]

并统计：

- slope
- variance
- max deviation
- final drift
- area under drift curve
- local spike count

### Natural Speech Control

必须加入真人语音作为 control。

核心问题：

> 真人连续读 20–30 分钟，本身会不会产生 embedding drift？

比较：

\[
Drift_{TTS}(t)
\]

与：

\[
Drift_{Human}(t)
\]

进一步定义：

\[
ExcessDrift(t)=Drift_{TTS}(t)-Drift_{Human}(t)
\]

这比简单 `Drift(t)` 更有科研价值。

### Multi-Evaluator

至少使用两个不同 speaker evaluator。

要求：

- 相同音频
- 相同分段
- 相同 reference strategy
- 分别计算 trajectory
- 检查趋势相关性

如果一个 evaluator 发现明显 drift，另一个没有，则不能直接宣称存在 speaker degradation。

### 初步实验规模

建议 pilot：

- 3 个 TTS generators
- 5 个 speakers
- 50–100 sentences / speaker
- 1 组 natural speech control
- 2 个 speaker evaluators

### Week 2 关键输出

- Speaker trajectory figure
- Human vs TTS comparison
- Multi-evaluator agreement
- Excess Drift 指标
- 初步 bootstrap CI

### Week 2 Research Gate

继续深入的条件：

- 至少一个 generator 存在稳定 trajectory
- 结果不是单一 evaluator artifact
- 与 human control 有可解释差异

否则：

- 检查 segmentation
- 检查 phonetic content
- 检查 reference strategy
- 保留负结果

---

## Week 3 — Prosody Trajectory

### 核心问题

> 长文本 TTS 的 prosody 是否随生成位置发生系统性变化？

不要将 prosody 简化为单个 F0。

### 多维指标

至少包括：

- F0 mean
- F0 std
- pitch range
- energy mean
- energy std
- speech rate
- pause ratio
- pause duration
- voiced ratio
- segment duration
- intensity
- rhythm-related statistics

可选：

- emotion / speaking style representation
- learned prosody embedding

### 轨迹形式

每个指标都表示为：

\[
P_k(t)
\]

而不是只有全局平均值。

建立：

```text
Pitch trajectory
Energy trajectory
Rate trajectory
Pause trajectory
Duration trajectory
```

然后考虑：

- DTW
- correlation
- smoothness
- slope
- changepoint
- variance growth

### Week 3 输出

- 多维 prosody trajectory
- Human/TTS baseline comparison
- 指标相关性矩阵
- 哪些指标最敏感
- 哪些指标可能冗余

---

## Week 4 — Evaluator Reliability

### 核心问题

> 我们观察到的 drift 到底是真实生成失效，还是 evaluator 本身造成的？

这一周不追求新的 benchmark 功能，重点是验证已有指标。

### 实验 1：Multi-Evaluator Agreement

比较：

- Pearson / Spearman correlation
- trajectory shape similarity
- rank consistency

### 实验 2：Phonetic / Text Control

检查：

> 不同 phonetic content 是否会制造 speaker similarity 假波动？

控制：

- 相同文本
- 相似文本长度
- 不同 phoneme distribution

### 实验 3：Channel Artifact

加入：

- codec
- noise
- resampling
- volume variation

观察：

\[
Drift_{clean}(t)
\]

与：

\[
Drift_{channel}(t)
\]

如果轻微 channel 扰动就制造巨大 drift，则该 evaluator 不适合作为核心指标。

### 实验 4：Reference Strategy

比较：

```text
first segment as reference
mean early-window embedding
global speaker centroid
```

避免结果完全依赖参考点选择。

### Week 4 输出

形成：

> **Evaluator Reliability Report**

明确：

- 哪些 metric 可以进入最终 benchmark
- 哪些只能作为辅助证据
- 哪些应该删除

---

## Week 5 — Temporal Failure Taxonomy

### 核心问题

> 长文本 TTS 的失效是否只有“逐渐漂移”一种形式？

设计：

#### Type A — Cumulative Drift

```text
────────╱╱╱╱╱
```

#### Type B — Abrupt Failure

```text
────────────╲____
```

#### Type C — Oscillation

```text
──╱╲──╱╲─╱╲──
```

#### Type D — Recovery

```text
────╲____╱────
```

#### Type E — Stable

```text
────────────────
```

### 建议指标

- global slope
- local slope
- max deviation
- changepoint count
- changepoint magnitude
- recovery time
- oscillation frequency
- local failure count
- AUC of deviation

### Week 5 输出

- Failure taxonomy
- 自动检测 prototype
- 典型案例图
- 每个 generator 的 failure profile

---

## Week 6 — Generator Architecture + Robustness

### 核心问题

> 不同 TTS 生成范式是否具有不同的长时程失效模式？

尽量按照生成机制分组：

```text
AR
NAR
Flow
Diffusion
Streaming
Non-streaming
```

具体取决于最终可获取模型。

### Robustness

加入：

- MP3 / AAC
- Noise
- Reverb
- Resampling
- Volume variation
- Unseen text
- Unseen speaker

如果资源允许，再加入：

- unseen generator

### Generator Attribution 的新定位

Generator Attribution 不再作为独立核心 RQ，只保留为辅助分析：

> **Temporal failure profile 是否本身具有 generator-specific 信息？**

如果没有信号，就删除，不影响主线。

### Week 6 输出

- Generator × Failure-type matrix
- Architecture-level comparison
- Clean vs OOD trajectory
- 辅助 attribution 实验（可选）

---

## Week 7 — Final Experiments + Human Validation + Statistics

### 目标

这一周不再开发主要功能，只：

> **冻结 protocol，扩大实验。**

### 建议最终规模

资源允许的情况下：

- 3–5 generators
- 10–20 speakers
- 100+ sentences / speaker
- natural speech control
- 多种 acoustic condition

### Human Validation

不需要做大型 MOS 众测。

可以做小规模人工验证：

- 抽取最稳定片段
- 抽取最严重 drift 片段
- 抽取 evaluator disagreement 片段
- 进行 pairwise identity / prosody consistency 判断

目的：

> 验证 automatic trajectory 是否与人的感知方向一致。

### 统计

至少包括：

- Mean
- Standard deviation
- Bootstrap 95% CI
- Effect size
- Pearson / Spearman correlation
- Appropriate paired tests
- Multiple comparison correction（如果大量比较）

### 必须记录

每个实验：

```text
config
seed
dataset version
generator version
evaluator version
commit hash
raw metrics
figure source data
```

---

## Week 8 — Paper / Benchmark / GitHub

### 最终研究故事

不是：

```text
我做了很多TTS指标
```

而是：

```text
传统评测通常把utterance作为独立样本
              ↓
可能忽略long-form generation中的时序失效
              ↓
我们把quality表示为trajectory
              ↓
研究speaker / prosody / failure event
              ↓
同时验证evaluator本身是否可靠
              ↓
比较不同generator的long-horizon failure pattern
```

### 最终报告结构

建议：

1. Introduction
2. Related Work
3. Problem Formulation
4. AudiobookBench-CN
5. Temporal Reliability Metrics
6. Evaluator Reliability
7. Experiments
8. Failure Taxonomy
9. Generator Comparison
10. Human Validation
11. Limitations
12. Conclusion

---

# 五、第一周日计划

> **Week 1 的唯一目标：真实数据 + 可重复 Pipeline + Evaluator Sanity Check。**

## Day 1 — 项目体检

让 Codex：

- 检查全部文件
- 检查 import / dependency
- 检查缺失脚本
- 找出 synthetic / mock / random data
- 检查 README 与代码是否一致
- 判断哪些模块保留、重写或进入 legacy
- 检查现有 speaker/prosody 指标是否真的接入真实数据
- 标记所有“VALIDATED / benchmark / robust”等可能过度声明

产物：

```text
AUDIT.md
```

不要第一天就重写项目。

## Day 2 — 项目重构

建立：

```text
legacy/
src/
configs/
data/
experiments/
results/
tests/
```

其中：

```text
src/
├── preprocessing/
├── features/
├── evaluators/
├── evaluation/
└── utils/
```

验收：

```bash
python -m pytest
```

基础测试能运行。

## Day 3 — Real Audio Pipeline

建立：

```text
data/
├── raw/
├── manifests/
├── natural_control/
└── processed/
```

manifest 至少包含：

```text
audio_path
source_type
generator
generator_family
speaker
text_id
sentence_id
position
duration
sample_rate
split
```

其中：

```text
source_type = synthetic / natural
```

必须至少成功处理：

**20–50 条真实音频。**

禁止使用随机音频作为最终实验输入。

## Day 4 — Speaker Evaluator Interface

建立统一接口：

```text
audio
 ↓
VAD
 ↓
segment
 ↓
speaker evaluator
 ↓
embedding
```

至少支持两个 evaluator，并实现：

```python
cosine_similarity()
speaker_representation_drift()
```

暂时不要命名为：

```python
identity_drift()
```

## Day 5 — Prosody Pipeline

建立：

```text
audio
 ↓
VAD
 ↓
F0
 ↓
Energy
 ↓
Duration
 ↓
Pause
 ↓
Speech Rate
 ↓
Prosody Features
```

至少得到：

```text
f0_mean
f0_std
pitch_range
energy_mean
energy_std
speech_rate
pause_ratio
duration
voiced_ratio
```

随机检查音频，确认结果不是：

```text
NaN
0
constant
```

## Day 6 — Evaluation Framework

建立：

```text
src/evaluation/
├── trajectory.py
├── speaker_drift.py
├── prosody.py
├── dtw.py
├── changepoint.py
└── statistics.py
```

建立：

```text
experiments/
└── exp01_speaker_trajectory/
    ├── config.yaml
    ├── run.py
    └── README.md
```

执行：

```bash
python experiments/exp01_speaker_trajectory/run.py
```

能够生成结果。

## Day 7 — Week 1 Gate

完整检查：

- [ ] 真实音频可以读取
- [ ] Natural / Synthetic metadata 能区分
- [ ] VAD 正常
- [ ] F0 正常
- [ ] 两个 speaker evaluator 至少能运行
- [ ] speaker representation drift 可以计算
- [ ] Prosody features 可以保存
- [ ] trajectory 可以保存
- [ ] Results 可以保存
- [ ] 实验可以重复运行
- [ ] evaluator 版本可以追踪
- [ ] 基础测试通过

最终报告：

```text
WEEK1_REPORT.md
```

内容：

1. Dataset
2. Pipeline
3. Evaluators
4. Feature Extraction
5. Initial Sanity Check
6. Known Risks
7. Week 2 Plan

---

# 六、Research Gate

```text
Week 1
  │
  └── Pipeline与Evaluator是否可靠？
          │
          ↓
Week 2
  │
  └── Speaker trajectory是否超过Natural Control？
       │
       ├── Yes → 深入
       ├── Weak → 保留并转向Prosody
       └── No → 检查Evaluator / 保留负结果
          │
          ↓
Week 3
  │
  └── 是否存在稳定的Prosody trajectory变化？
          │
          ↓
Week 4
  │
  └── 这些现象是否跨Evaluator / Channel稳定？
       │
       ├── Stable → 进入Failure Taxonomy
       └── Unstable → 缩小Claim
          │
          ↓
Week 5
  │
  └── 能否形成可重复Failure Taxonomy？
          │
          ↓
Week 6
  │
  └── Failure pattern是否具有Generator/Architecture差异？
          │
          ↓
Week 7
  │
  └── Final Experiment + Human Check
          │
          ↓
Week 8
  │
  └── Paper / Benchmark / GitHub
```

---

# 七、重要止损线

## Week 1 不做

- ❌ 大规模实验
- ❌ 论文写作
- ❌ 复杂模型
- ❌ 漂亮网页
- ❌ 实验室关键词包装
- ❌ 为了贴某篇论文硬塞模块
- ❌ 复杂 DTW 优化
- ❌ 长时间 brute-force sweep
- ❌ 追求漂亮结果
- ❌ 把单个 embedding 指标当作真实 identity ground truth

## 整个 8 周都不做

- ❌ 为得到显著结果反复调 protocol
- ❌ 使用 mock / synthetic 结果支撑正式 claim
- ❌ 将 correlation 写成 causation
- ❌ 将 evaluator score 直接等同于 human perception
- ❌ 把所有模块都包装成“创新点”

---

# 八、最终成果目标

8 周结束后，理想状态下拥有：

## 1. 一个明确研究主题

**AudiobookBench-CN**

> *A Benchmark for Temporal Reliability in Long-form Text-to-Speech*

## 2. 一个核心研究贡献

不是：

> “增加更多 TTS metrics。”

而是：

> **将长文本 TTS 评价从 utterance-level scalar evaluation 扩展为 temporal trajectory evaluation。**

## 3. 三类核心分析

```text
Speaker Representation Trajectory
              ↓
Prosody Trajectory
              ↓
Temporal Failure Taxonomy
```

## 4. 一个 Evaluator Reliability Layer

```text
Natural Control
      +
Multi-Evaluator
      +
Channel Robustness
      +
Human Validation
```

## 5. 一个 Generator Comparison Layer

重点回答：

> 不同 generation paradigms 是否具有不同 long-horizon failure modes？

Generator Attribution 仅作为可选辅助实验。

## 6. 一份完整科研报告

目标：

**8–12 页**

## 7. 一个可复现 GitHub 项目

别人拿到：

- 代码
- config
- manifest
- evaluator version
- experiment protocol
- figure source data

后，可以理解并复现核心实验。

---

# 九、时间投入建议

如果每天约 2–4 小时：

```text
Week 1   ████        Pipeline / Evaluator
Week 2   █████       Speaker + Natural Control
Week 3   █████       Prosody Trajectory
Week 4   █████       Evaluator Reliability
Week 5   █████       Failure Taxonomy
Week 6   █████       Generator / Robustness
Week 7   ██████      Final Experiments + Human Check
Week 8   █████       Paper / Benchmark / GitHub
```

---

# 十、最终判断标准

项目成功不等于：

> “证明长文本 TTS 一定会漂移。”

以下结果都可以是成功科研结果：

### Outcome A

发现稳定、可重复的 long-horizon degradation。

### Outcome B

只有某些维度发生变化，例如 prosody 明显变化，但 speaker representation 基本稳定。

### Outcome C

所谓 speaker drift 主要来自 evaluator / phonetic content / channel artifact。

### Outcome D

不同 generator 没有统一退化方向，但存在不同 temporal failure pattern。

### Outcome E

在当前数据和评测协议下，没有发现显著 long-horizon degradation。

最重要的是：

> **实验设计能够区分“生成系统真的退化”与“评测器制造了退化假象”。**

这将比单纯得到一张向上漂移的曲线更有研究价值。
