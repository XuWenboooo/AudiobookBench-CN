#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_all_optimizations.py - AudiobookBench 自动化优化与学术增强全流程调度器
一键串联：
1. 创新点 A/B/C 增强路线：自然句对照集 -> 情感轨迹 DTW 评估 -> 探针 v3 增广
2. P1 必修声学缺陷校正：F0 基频提取器与双门限 VAD 唤醒校正 (剔除首尾静音垫)
3. P2 长文本工业创新点：角色音色长程估计 (Speaker Drift) 评估器
4. 南开秦勇实验室三层前沿体系：AS-70 破句与非流利惩罚 + CWT 多尺度重音 + IPR 模糊语气 + FELLE 时序连贯度
5. P2 工程提效工具：学术级 LaTeX 四大三线表自动生成与格式化器
"""
import sys
import subprocess
from pathlib import Path

BENCH_DIR = Path(__file__).resolve().parent

TASKS = [
    ("自然句对照集抽取 (创新点A)", BENCH_DIR / "build_natural_contrast.py"),
    ("帧级情感轨迹 DTW 评估 (创新点B)", BENCH_DIR / "emotion_trajectory_dtw.py"),
    ("合成器归因探针 v3 (创新点C)", BENCH_DIR / "probe_attribution_v3.py"),
    ("F0 提取与 VAD 唤醒校正 (P1 必修声学修复)", BENCH_DIR / "f0_vad_calibrator.py"),
    ("角色音色长程估计评估器 (P2 工业痛点新方法)", BENCH_DIR / "speaker_drift_evaluator.py"),
    ("南开前沿三层停顿与语气评估引擎 (AS-70/IPR/FELLE)", BENCH_DIR / "nankai_prosody_engine.py"),
    ("LaTeX 三线表自动返回器 (P2 工程提效加速成稿)", BENCH_DIR / "latex_table_formatter.py"),
]

def main():
    print("=" * 75)
    print("🚀 启动 AudiobookBench-CN 优化落地与学术工具全链路自动调度器")
    print("=" * 75)

    all_ok = True
    for name, script_path in TASKS:
        print(f"\n▶️ [调度执行]: {name} ({script_path.name})")
        if script_path.exists():
            ret = subprocess.run([sys.executable, str(script_path)])
            if ret.returncode != 0:
                print(f"❌ 任务失败: {name}, 退出码: {ret.returncode}")
                all_ok = False
                break
        else:
            print(f"⚠️ 找不到脚本: {script_path}")
            all_ok = False
            break

    print("\n" + "=" * 75)
    if all_ok:
        print("🎉 全部七项核心优化脚本与学术工程工具执行完毕，数据产物已全部就绪！")
        print("📁 生成的关键数据与 LaTeX 片段:")
        print("  - manifest_natural_contrast.json")
        print("  - emotion_trajectory_results.json")
        print("  - probe_v3_results.json")
        print("  - f0_vad_calibrated_result.json")
        print("  - speaker_drift_results.json")
        print("  - nankai_prosody_evaluation.json")
        print("  - audiobookbench_tables.tex (含四大标准三线表，可直接 \\input{} 到论文)")
    else:
        print("⚠️ 部分任务执行中断，请检查具体日志。")
    print("=" * 75)

if __name__ == "__main__":
    main()
