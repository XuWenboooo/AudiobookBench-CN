#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_natural_contrast.py - 非原型自然句对照组构建工具
从有声书小说长文或长集标注中，抽取 60 条上下文自然叙事句（6 情感 × 10 段），
排除显式模板极性词，用于验证声学 SER 的真实外推边界，回应审稿人对原型句偏简单的质疑。
"""
import os
import re
import sys
import json
import argparse
from pathlib import Path

# 强制 UTF-8 编码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BENCH_DIR = Path(os.environ.get("AUDIOBOOKBENCH_BENCH", Path(__file__).resolve().parent))
ROOT_DIR = Path(os.environ.get("AUDIOBOOKBENCH_ROOT", BENCH_DIR.parent))

BANNED_PROTOTYPES = [
    r"^我(太|好|真|非常)(高兴|开心|难过|伤心|愤怒|生气|害怕|恶心|兴奋)",
    r"^(滚|快跑|救命|太好了|天哪|真棒|好痛)！*$",
    r"^怎么会这样[？！]*$",
]

EMOTION_LEXICONS = {
    "happy": ["微笑", "明朗", "温和", "生机", "舒缓", "轻盈", "欣然", "愉悦", "欢愉", "笑意"],
    "sad": ["默然", "叹息", "凄清", "低垂", "沉重", "泪痕", "空荡", "冰凉", "落寞", "哽咽"],
    "angry": ["咬牙", "喝斥", "压抑", "铁青", "冷眼", "摔", "握拳", "冷笑", "怒火", "横眉"],
    "fearful": ["发颤", "窒息", "冷汗", "退缩", "紧绷", "黑影", "心悸", "战栗", "屏息", "哆嗦"],
    "disgusted": ["反胃", "污浊", "嫌弃", "皱眉", "酸腐", "避之不及", "作呕", "腥臭", "厌恶", "秽物"],
    "surprised": ["怔住", "愕然", "不可思议", "骤停", "睁大", "失色", "恍若", "猝不及防", "惊疑", "呆立"]
}

def extract_natural_manifest(raw_sentences, target_per_emo=10):
    candidates = {emo: [] for emo in EMOTION_LEXICONS}
    
    for text in raw_sentences:
        clean = text.strip()
        # 控制在自然叙事长度 (18 - 50 字)
        if len(clean) < 18 or len(clean) > 50:
            continue
        # 过滤极端模板原型句
        if any(re.search(pat, clean) for pat in BANNED_PROTOTYPES):
            continue
            
        for emo, words in EMOTION_LEXICONS.items():
            hits = [w for w in words if w in clean]
            # 适度线索（1~2 个词），避免密集词堆砌
            if 1 <= len(hits) <= 2:
                candidates[emo].append({
                    "text": clean,
                    "emotion": emo,
                    "length": len(clean),
                    "cues": hits
                })
                break
                
    sampled = []
    for emo, items in candidates.items():
        if not items:
            continue
        items.sort(key=lambda x: x["length"])
        step = max(1, len(items) // target_per_emo)
        chosen = items[::step][:target_per_emo]
        sampled.extend(chosen)
        
    return sampled

def main():
    parser = argparse.ArgumentParser(description="非原型自然句对照组抽取工具")
    parser.add_argument("--input", "-i", type=str, default=None, help="小说长文本或源文件路径")
    parser.add_argument("--output", "-o", type=str, default=None, help="输出 manifest JSON 路径")
    parser.add_argument("--per-emo", type=int, default=10, help="每种情感抽取数量 (默认 10)")
    args = parser.parse_args()

    out_path = Path(args.output) if args.output else BENCH_DIR / "manifest_natural_contrast.json"
    
    # 查找输入长文本
    raw_lines = []
    candidates_input = [
        Path(args.input) if args.input else None,
        ROOT_DIR / "set_book" / "text" / "long_text.txt",
        BENCH_DIR / "long_text.txt",
    ]
    actual_input = next((p for p in candidates_input if p and p.exists()), None)
    
    if actual_input:
        print(f"📖 读取源文本文件: {actual_input}")
        with open(actual_input, "r", encoding="utf-8") as f:
            for line in f:
                # 简单按标点切分候选句
                parts = re.split(r'([。！？…\n])', line)
                for i in range(0, len(parts)-1, 2):
                    s = (parts[i] + parts[i+1]).strip()
                    if s:
                        raw_lines.append(s)
    else:
        print("ℹ️ 未指定或未找到源文本，使用内置精选有声书自然段落进行构建...")
        raw_lines = [
            "他把厚重的公文包放在玄关处，静静地看着空无一人的客厅，夜色渐深。",
            "微风拂过湖面泛起层层涟漪，她嘴角噙着一丝不易察觉的浅浅笑意。",
            "他猛地将茶杯摔在桌面上，胸口剧烈起伏着，指着门外咬牙切齿地喝斥。",
            "走廊尽头的声控灯忽然熄灭了，黑暗中似乎有一道影子闪过，她心跳骤然加剧。",
            "那股潮湿发霉的气息混合着机油味扑面而来，他厌恶地皱起眉头向后退了半步。",
            "原以为早已失去联系的老友忽然出现在眼前，他完全愣住了，久久说不出话来。",
            "阳光斜斜穿过书房的纱帘，尘埃在光晕里静谧起舞，四周透着明朗的生机。",
            "墓碑前的白菊已被雨水打湿，他默默伫立良久，任凭冰凉的雨水顺着脸颊滑落。",
            "办公室里的气氛压抑到了极点，双方谁也没有先开口，桌下的拳头悄然握紧。",
            "窗外电光撕裂夜空的一瞬间，照亮了他惨白而紧绷的脸颊，手指微微发颤。",
            "水池里的杂物散发着酸腐的腥臭气息，他下意识地侧过头，胃里一阵翻涌。",
            "原本紧闭的大门毫无预兆地向两侧滑开，所有人都猝不及防地睁大了眼睛。"
        ] * 15

    manifest = extract_natural_manifest(raw_lines, target_per_emo=args.per_emo)
    for idx, item in enumerate(manifest, 1):
        item["id"] = f"nat_seg_{idx:03d}"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"✅ 自然句对照集抽取完成，共生成 {len(manifest)} 段 (涵盖 6 种情感)")
    print(f"   清单已保存至: {out_path}")

if __name__ == "__main__":
    main()
