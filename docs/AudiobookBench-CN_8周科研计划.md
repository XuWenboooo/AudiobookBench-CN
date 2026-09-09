# AudiobookBench-CN：8 周科研计划

> **项目定位：** 长文本 TTS 的可信度与长程一致性评测基准  
> **核心问题：** 长文本 TTS 是否存在可测量、可重复、且具有生成器特异性的长程退化？  
> **建议周期：** 8 周  
> **建议投入：** 每周 15–25 小时

---

## 一、项目总体研究路线

```text
                    AudiobookBench-CN
                           │
              长文本 TTS 可信度评测
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
  Speaker Drift      Prosody Drift     Generator Attribution
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ↓
                 Long-range Reliability
                           │
                           ↓
                      Robustness
                           │
                           ↓
                  OOD / Real-world
```

### 三个核心研究问题

**RQ1 — Speaker Drift**

> 长文本 TTS 中，同一个角色的声音是否会随着生成位置增加而逐渐偏离？

**RQ2 — Prosody Drift**

> 长文本生成过程中，F0、Energy、语速、停顿和情绪/韵律轨迹是否发生系统性变化？

**RQ3 — Generator Attribution**

> 生成音频中是否存在稳定的、具有生成器特异性的 fingerprint？

---

# 二、8 周总计划

| 周 | 核心目标 | 主要工作 | 周末必须得到的成果 |
|---|---|---|---|
| **Week 1** | 🧱 工程重构 + 数据管线 | 清理现有代码、真实数据、metadata、VAD、F0、embedding 接口 | **真实数据 pipeline 跑通** |
| **Week 2** | 🎙️ Speaker Drift | 实现长文本说话人漂移指标，3 个 TTS generator 初测 | **第一张核心 Drift 曲线** |
| **Week 3** | 🎵 Prosody Drift | F0、Energy、语速、停顿、prosody trajectory、DTW | **Prosody 长程退化结果** |
| **Week 4** | 🧬 Generator Attribution | 判断是否存在生成器特异性 fingerprint | **Generator attribution baseline** |
| **Week 5** | 🔬 机制分析 | speaker/text/length/generator 因素拆解 + ablation | **解释“为什么会漂移”** |
| **Week 6** | 🛡️ Robustness / OOD | codec、noise、reverb、不同文本/说话人等 OOD | **可靠性/鲁棒性实验** |
| **Week 7** | 📊 大实验 + 统计 | 扩大数据量、Bootstrap CI、effect size、显著性、统一图表 | **最终实验结果集** |
| **Week 8** | 📄 科研成果整理 | README、论文式报告、图表、实验记录、GitHub | **完整研究项目 + 8–12 页报告** |

---

# 三、详细周计划

## Week 1 — 工程重构 + 真实数据 Pipeline

### 核心目标

把当前项目从“代码 Demo / synthetic experiment”变成：

> **真实音频 → preprocessing → features → evaluation → results**

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
- 建立 reproducibility 和基础测试

### 周末验收

```text
Real Audio
    ↓
Preprocessing
    ↓
Features
    ↓
Evaluation
    ↓
Results
```

必须能够完整跑通。

---

## Week 2 — Speaker Drift

### 核心问题

> 长文本 TTS 中，同一个角色的声音是否会随着文本位置增加而逐渐偏离？

### 基础指标

定义：

\[
Drift(t)=1-\cos(E_0,E_t)
\]

其中：

- \(E_0\)：开头 reference embedding
- \(E_t\)：第 t 个文本窗口 embedding

例如：

```text
Long-form text
│
├── 1–10 sentences   → E1
├── 11–20             → E2
├── 21–30             → E3
├── ...
└── 91–100            → E10
```

### 初步实验规模

建议：

- 3 个 TTS generators
- 5–10 个 speakers
- 50–100 sentences / speaker

### 关键输出

- Drift trajectory
- Generator 间比较
- Speaker 间比较
- 不同文本长度比较

### Research Gate

如果 Speaker Drift：

- **明显且稳定** → 继续深入
- **较弱** → 转向 Prosody Drift
- **基本不存在** → 保留负结果，并检查测量方法是否合理

---

## Week 3 — Prosody Drift

### 核心问题

> 长文本生成过程中，韵律是否发生系统性退化？

### 关注特征

- F0 mean / std
- Energy mean / std
- Speech rate
- Pause ratio
- Duration
- Pitch variance
- Intensity
- Emotion trajectory

### 方法

真实音频：

```text
Audio
 ↓
VAD
 ↓
F0 / Energy / Duration / Pause
 ↓
Frame / Segment trajectory
 ↓
DTW / Correlation / Smoothness
```

### 关键比较

```text
Short text
     ↓
Medium text
     ↓
Long text
```

以及：

```text
Generator A
Generator B
Generator C
```

---

## Week 4 — Generator Attribution

### 核心问题

> 能不能从生成音频中判断“是谁生成的”？

基础流程：

```text
Audio
 ↓
Acoustic Features
 ↓
Classifier
 ↓
Generator A / B / C
```

### 必须做的测试

#### 1. Seen Text

训练与测试文本分布相似。

#### 2. Unseen Text

训练文本与测试文本完全不同。

#### 3. Unseen Speaker

训练说话人与测试说话人不同。

#### 4. Perturbed Audio

```text
Clean
Codec
Noise
Reverb
```

### 重点

不要只报告 Accuracy。

要研究：

> Generator fingerprint 是否能够跨文本、speaker 和 channel 条件保持稳定？

---

## Week 5 — Mechanism Analysis

这一周从：

> **“发现现象”**

进入：

> **“解释现象”。**

### 重点因素

- Speaker
- Text
- Generator
- Text length
- Position
- Acoustic condition

### Ablation 示例

| 实验 | Speaker variation | Text variation | Generator | Length |
|---|---:|---:|---:|---:|
| Baseline | ✓ | ✓ | ✓ | ✓ |
| No speaker variation | ✗ | ✓ | ✓ | ✓ |
| Short text | ✓ | ✓ | ✓ | ↓ |
| Long text | ✓ | ✓ | ✓ | ↑ |
| Fixed generator | ✓ | ✓ | ✗ | ✓ |

### 核心问题

> Drift 到底主要来自 generator，还是 speaker / text / duration？

这一周决定项目的科研解释力。

---

## Week 6 — Robustness / OOD

### 加入真实世界扰动

- MP3 / AAC codec
- Noise
- Reverb
- Volume variation
- Sampling rate variation
- Unseen speaker
- Unseen text
- Unseen generator

### 比较

\[
Performance_{clean}
\rightarrow
Performance_{OOD}
\]

以及：

\[
Drift_{clean}
\rightarrow
Drift_{OOD}
\]

### 项目方向升级

这一阶段开始从：

> TTS Benchmark

进一步形成：

> **Trustworthy Speech Generation Evaluation**

---

## Week 7 — Final Experiments + Statistics

### 这周才扩大规模

建议：

- 3–5 generators
- 10–20 speakers
- 100+ sentences
- 多种 channel / OOD 条件

统一运行：

- Speaker Drift
- Prosody Drift
- Generator Attribution
- Robustness
- Ablation

### 统计分析

至少包括：

- Mean
- Standard deviation
- Bootstrap 95% CI
- Effect size
- Correlation
- Appropriate significance tests

### 原则

> **Week 7 不再开发大功能，主要负责收集最终数据。**

---

## Week 8 — 科研成果整理

### 最终项目结构

```text
AudiobookBench-CN/
│
├── README.md
├── configs/
├── data/
│   ├── raw/
│   ├── manifests/
│   └── processed/
│
├── src/
│   ├── preprocessing/
│   ├── features/
│   ├── evaluation/
│   └── baselines/
│
├── experiments/
│   ├── exp01_speaker_drift/
│   ├── exp02_prosody_drift/
│   ├── exp03_generator_attribution/
│   └── exp04_robustness/
│
├── results/
│   ├── figures/
│   ├── tables/
│   └── raw/
│
├── tests/
└── legacy/
```

### 最终科研报告

建议 8–12 页：

1. Introduction
2. Related Work
3. Research Questions
4. Dataset
5. Methodology
6. Experiments
7. Results
8. Ablation
9. Limitations
10. Conclusion

---

# 四、第一周日计划

> **Week 1 的唯一目标：真实数据 + 可重复 Pipeline。**

## Day 1 — 项目体检

### 任务

让 Codex：

- 检查全部文件
- 检查 import / dependency
- 检查缺失脚本
- 找出 synthetic / mock / random data
- 检查 README 与代码是否一致
- 判断哪些模块保留、重写或进入 legacy

### 产物

```text
AUDIT.md
```

### 注意

**不要第一天就让 Codex 重写项目。**

---

## Day 2 — 项目重构

建立：

```text
legacy/
src/
experiments/
configs/
data/
results/
tests/
```

将旧实验脚本放入：

```text
legacy/
```

建立：

```text
src/
├── preprocessing/
├── features/
├── evaluation/
└── utils/
```

### 验收

```bash
python -m pytest
```

基础测试能够运行。

---

## Day 3 — Real Audio Pipeline

建立：

```text
data/
├── raw/
├── manifests/
└── processed/
```

manifest 至少包含：

```text
audio_path
generator
speaker
text_id
sentence_id
duration
sample_rate
split
```

建立：

```text
audio
 ↓
load
 ↓
resample
 ↓
normalize
 ↓
VAD
 ↓
metadata
```

### 验收

至少成功处理：

**20–50 条真实音频。**

禁止用随机音频代替。

---

## Day 4 — Speaker Feature

建立：

```text
audio
 ↓
VAD
 ↓
segment
 ↓
speaker embedding
 ↓
embedding.npy
```

实现：

```python
cosine_similarity()
drift()
```

即：

```python
drift = 1 - cosine_similarity(reference, current)
```

### 验收

先使用：

**5 speakers × 若干音频**

确认 embedding pipeline 正常。

---

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
Prosody Features
```

至少得到：

```text
f0_mean
f0_std
energy_mean
energy_std
speech_rate
pause_ratio
duration
```

### 验收

随机检查几个音频，确认结果不是：

```text
NaN
0
constant
```

---

## Day 6 — Evaluation Framework

把前几天模块连接起来：

```text
Audio
 ↓
Preprocessing
 ↓
Speaker Features
 ↓
Prosody Features
 ↓
Evaluation
 ↓
Results
```

建立：

```text
src/evaluation/
├── cosine.py
├── drift.py
├── dtw.py
└── statistics.py
```

建立：

```text
experiments/
└── exp01_speaker_drift/
    ├── config.yaml
    ├── run.py
    └── README.md
```

### 验收

可以执行：

```bash
python experiments/exp01_speaker_drift/run.py
```

并生成结果。

---

## Day 7 — Week 1 Gate

### 完整检查

- [ ] 真实音频可以读取
- [ ] VAD 正常
- [ ] F0 正常
- [ ] Speaker embedding 正常
- [ ] Drift 可以计算
- [ ] Prosody features 可以保存
- [ ] Results 可以保存
- [ ] 实验可以重复运行
- [ ] 基础测试通过

### 最终目录

```text
results/
├── speaker_embeddings/
├── prosody/
├── metrics/
└── logs/
```

### 最终报告

```text
WEEK1_REPORT.md
```

内容：

1. Dataset
2. Pipeline
3. Feature extraction
4. Speaker embedding
5. Initial sanity check
6. Problems
7. Week 2 plan

---

# 五、8 周项目的 Research Gate

每周结束都不要默认继续原计划，而是根据实验结果决定下一步。

```text
Week 1
  │
  └── Pipeline 是否可靠？
          │
          ↓
Week 2
  │
  └── Speaker Drift 是否存在？
       │
       ├── Strong → 深入
       ├── Weak   → 转向 Prosody
       └── None   → 检查指标 / 保留负结果
          │
          ↓
Week 3
  │
  └── Prosody Drift 是否存在？
          │
          ↓
Week 4
  │
  └── Generator fingerprint 是否稳定？
          │
          ↓
Week 5
  │
  └── 找机制
          │
          ↓
Week 6
  │
  └── OOD / Robustness
          │
          ↓
Week 7
  │
  └── Final experiment
          │
          ↓
Week 8
  │
  └── Research report / GitHub
```

---

# 六、重要止损线

## Week 1 不做

- ❌ 大规模实验
- ❌ 论文写作
- ❌ 复杂模型
- ❌ 漂亮网页
- ❌ Nankai lab keyword packaging
- ❌ AS-70 / IPR / FELLE 核心开发
- ❌ 复杂 DTW 优化
- ❌ 8 小时计算
- ❌ 追求漂亮结果

## Week 1 只追求

> **真实数据 + 可重复 Pipeline + 第一套可信指标。**

---

# 七、最终成果目标

8 周结束后，理想状态下拥有：

### 1. 完整科研项目

**AudiobookBench-CN**

### 2. 清晰研究问题

> 长文本 TTS 是否存在可测量、可重复、且具有生成器特异性的长程退化？

### 3. 三个核心实验

```text
Speaker Drift
      ↓
Prosody Drift
      ↓
Generator Attribution
```

### 4. Robustness Layer

```text
Clean
 ↓
Codec
 ↓
Noise
 ↓
Reverb
 ↓
Unseen Generator
```

### 5. 一份完整科研报告

目标：

**8–12 页**

### 6. 一个可复现 GitHub 项目

要求：

> 别人拿到代码、配置和数据说明后，可以理解并复现核心实验。

---

# 八、时间投入建议

如果每天约 2–4 小时：

```text
Week 1   ████        工程 / 数据
Week 2   █████       Speaker Drift
Week 3   █████       Prosody
Week 4   █████       Attribution
Week 5   ████        Mechanism
Week 6   ████        Robustness
Week 7   ██████      Final Experiments
Week 8   █████       Paper / Portfolio
```

### 最重要的两个节点

**Week 1：** Pipeline Gate  
> 能不能真正做实验？

**Week 2：** Research Gate  
> Speaker Drift 是否真的存在？

如果第二周发现假设不成立，不要硬做。**科研项目允许负结果，最忌讳为了“做出结果”而修改实验设计迎合预期。**
