# AudiobookBench-CN 落地增强与学术工程套件使用指引

本工具包涵盖基准代码库底层漏洞修复、长文本工业痛点评估、南开大学秦勇实验室前沿体系演进，以及学术成稿自动化三线表工具。

---

## 🛠️ 模块体系与理论对标

### 1. 南开大学秦勇实验室启发：三层停顿与语气进阶评估引擎 (`nankai_prosody_engine.py`)
- **[短期 Tier 1] AS-70 数据集与非流利/口吃事件检测 (SED) 理论对标**：
  - **韵律断裂与破句惩罚器 (Chopping Penalty)**：检测句内非标点位置异常停顿、长音卡顿拉长（Prolongation），输出标点契合度 `Break F1` 与破句率；
  - **连续小波变换 (CWT) 多尺度焦点重音 (Focus Prominence)**：将 F0 分解为宏观意群、中观词焦点与微观音节层，量化句子重心重音突显强度。
- **[中期 Tier 2] IPR (Iterative Prototype Refinement for Ambiguous SER) 理论对标**：
  - **多原型模糊语气软对齐 (Iterative Prototype Tone Alignment)**：摒弃单一粗糙 8 分类，采用软亲和度分布与信息熵建模复合戏感；
  - **声门发声态物理声学 ($H1-H2$)**：提取频谱第一/第二谐波差，区分常态音 (Modal)、气化低语 (Breathy) 与紧喉压音 (Pressed/Creaky)。
- **[长期 Tier 3] FELLE (Autoregressive Flow Matching with Stepwise Prior) 理论对标**：
  - **步进先验时序演进连贯性 (Temporal Coherence Score, TCS)**：评估自回归长段落演播中前后句韵律流式迁移的光滑性与一致性。

### 2. P1 (必修声学缺陷修复) (`f0_vad_calibrator.py`)
- **NCCF 物理基频提取**：严格浊音（Voiced/Unvoiced）门限判决，消除全音频无声段伪峰，提取半音标准差与动态范围；
- **双门限双向 VAD 唤醒校正**：前向回溯与后向裁剪，彻底消除 TTS 首尾 0.5s~1.2s 无效静音垫，恢复真实字语速（char/s）与有效停顿比。

### 3. P2 (长文本工业新方法) (`speaker_drift_evaluator.py`)
- **角色音色长程漂移评估**：针对多角色连续 30+ 句长篇演播，度量锚点漂移率 ($\Delta_{\text{anchor}}$)、自回归衰退斜率 ($\beta$)、阶跃抖动、角色原型隔离裕量 (Margin) 与串音混淆率。

### 4. P2 (工程提效工具) (`latex_table_formatter.py`)
- **LaTeX 标准三线表自动生成**：生成符合 ACL/EMNLP/Interspeech 规范的 `booktabs` 源码，支持极性推断、最优加粗、次优下划线，输出四大三线表（主基准表、长程漂移表、声学校准消融表、南开三层韵律语气对比表）。

### 5. 原有三项优化基石
- `build_natural_contrast.py`：非原型自然句对照集抽取（创新点 A）
- `emotion_trajectory_dtw.py`：帧级情感轨迹 DTW 评估器（创新点 B）
- `probe_attribution_v3.py`：带 Codec 增广的合成器溯源线性探针（创新点 C）

---

## 🚀 一键运行与交付产物

在命令行直接运行调度器：

```bash
python run_all_optimizations.py
```

执行后将自动生成全部核心数据产物与 LaTeX 源码：
- `nankai_prosody_evaluation.json`
- `f0_vad_calibrated_result.json`
- `speaker_drift_results.json`
- `manifest_natural_contrast.json`
- `emotion_trajectory_results.json`
- `probe_v3_results.json`
- `audiobookbench_tables.tex`（可直接在论文中 `\input{audiobookbench_tables.tex}`）
